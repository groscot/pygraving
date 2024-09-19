# from enum import Enum

from ..config import config
from ..note import Note
from ..score import Score
from . import parse_input

# class State(Enum):
#     INIT = 0
#     RUNNING = 1
#     PAUSED = 2
#     STOPPED = 3
#     FINISHED = 4

def unstack_arguments(args: list):
    "Take a list of argument, value (even length) and return a dictionary"
    result = {}
    for i in range(0, len(args), 2):
        result[args[i]] = args[i+1]
    return result


class StateMachine:
    # state: State = State.INIT
    
    def __init__(self) -> None:
        self.override_config = {}
        score = Score()
        self.score = score
        self.active_duration = 2
        self.active_scoreline = None
        self.selected_object = None
        self.selected_type = None
        self.slur_start = None
        self.last_position = 0 #! WARNING will be problematic if multiple lines and switching between them
    
    def __call__(self, text_input: str):
        parsed_tokens = parse_input(text_input)
        self.run(parsed_tokens)
        with config.temporary_override(**self.override_config):
            return self.score.finalize()
    
    @property
    def active_duration_in_spaces(self):
        return max(4/(2**self.active_duration), 1)
    
    def forward(self, amount: int = None):
        amount = amount or self.active_duration_in_spaces
        self.last_position += amount
    
    def backward(self, amount: int = None):
        amount = amount or self.active_duration_in_spaces
        self.last_position -= amount
    
    def run(self, parsed_tokens: list):
        for token in parsed_tokens:
            self.process_token(token)
    
    def process_token(self, token):
        original_token = token
        token = token.asDict()
        if "command" in token:
            self.process_command(token)
            return
        if "config" in token:
            param = token["param"]
            value = token["value"]
            if hasattr(config, param):
                self.override_config[param] = value
            return
        if "bar" in token:
            self.active_scoreline.register("bar", position=self.last_position, style=token["bar"])
            self.forward(1)
            return
        if "silence" in token:
            self.active_scoreline.register("silence", position=self.last_position, duration=self.active_duration)
            self.forward()
            return
        if "note" in token:
            self.process_note(token)
            return
        if "chord" in token:
            self.active_scoreline.register(
                "chord", notes=token["chord"]["notes"], duration=self.active_duration, position=self.last_position, up="flipped" not in token["chord"],
            )
            for i, note_token in enumerate(token["chord"]["notes"]):
                self.process_slur_if_present(note_token, position=self.last_position+i)
            self.forward()
            return
        if "beam" in token:
            self.active_scoreline.register(
                "beamed_group", notes=token["beam"]["notes"], duration=1, position=self.last_position, up="flipped" not in token["beam"],
            )
            for i, note_token in enumerate(token["beam"]["notes"]):
                self.process_slur_if_present(note_token, position=self.last_position+i)
            self.forward( len(token["beam"]["notes"]) )
            return
        else:
            print("Unknown token", original_token)
        
    def process_command(self, token):
        if token["command"] == "BEGIN":
            if token["object"] == "line":
                self.active_scoreline = self.score.add_scoreline()
                self.last_position = 0
            elif token["object"] == "grouped":
                grouped_lined = self.score.add_scoreline(grouped_with=self.active_scoreline)
                self.active_scoreline = grouped_lined
                self.last_position = 0
            else:
                raise ValueError("Unknown object: " + token["object"])
        elif token["command"] == "SET":
            if token["param"] == "duration":
                self.active_duration = token["value"]
            elif token["param"].startswith("clef_"):
                which = token["param"].split("_")[1]
                self.active_scoreline.register("clef_alterations", type=which, number=token["value"])
            else:
                raise ValueError("Unknown param: " + token["param"] + "in " + str(token))
        elif token["command"] == "END":
            print("END command has no effect")
        elif token["command"] == "MOVE":
            sign = -1 if token["direction"].lower() == "back" else 1
            self.forward(sign * token["amount"])
        elif token["command"] == "SIGNATURE":
            value = token["value"]
            if "C" in value:
                self.active_scoreline.register("signature", is_C=True)
            else:
                self.active_scoreline.register("signature", **value[0])
        elif token["command"] == "PLACE":
            what = token["object"]
            args = unstack_arguments(token["arguments"])
            if "position" not in args:
                args["position"] = self.last_position
            duration = args.get("duration", self.active_duration)
            if what in ["note", "chord"] and "duration" not in args:
                args["duration"] = duration
            try:
                self.active_scoreline.register(what, **args)
            except:
                raise ValueError("Unknown object for PLACE: " + what)
        elif token["command"] == "SELECT":
            return self.process_select(token)
        elif token["command"] == "TRANSLATE":
            x = token["x"]
            y = token["y"]
            if self.selected_object is None:
                raise ValueError("No object selected for translation")
            note = self.selected_object
            note.selection[self.selected_type] |= {
                "x": x,
                "y": y,
            }
        else:
            raise ValueError("Unknown command: " + token["command"])
    
    def process_select(self, token):
        """What can be selected:
        - note modifier
        - note fingering
        - silence
        - in the future: slur, tie, etc.
        Basically symbols that are not part of the note itself, but are related to it.
        """
        target = token["object"]
        if target.startswith("(("):
            target_type = "fingering_string"
            target_value = int(target[2])
        elif target.startswith("("):
            target_type = "fingering_finger"
            target_value = int(target[1])
        elif target == "_":
            target_type = "silence"
            target_value = None
        elif target == ".":
            target_type = "dot"
            target_value = None
        else:
            target_type = "modifier"
            target_value = target
        for what, args in reversed(self.active_scoreline.layout.registered):
            if what not in ["note", "chord", "silence"]:
                continue
            if what == "note":
                note: Note = args["note"]
                success = self.inspect_note_for_selection(note, target_type, target_value)
                if success:
                    self.selected_object = note
                    self.selected_type = target_type
                    note.selection[target_type] = {
                        "value": target_value,
                    }
                    return
            # if target in note.extras:
            #     note.extras[target] = True
            #     return
    
    def inspect_note_for_selection(self, note: Note, target_type: str, target_value: str|int|None):
        if target_type.startswith("fingering"):
            return note.extras.get(target_type, None) == target_value
        if target_type == "dot":
            return note.is_dotted
        if target_type == "modifier":
            return target_value in note.modifiers
        if target_type == "silence":
            raise NotImplementedError("Silence selection not implemented")
    
    def process_note(self, token):
        note = Note.from_token(token["note"])
        note.duration = self.active_duration
        self.active_scoreline.register("note", note=note, position=self.last_position)
        
        if "slur_start" in token["note"]:
            self.slur_start = (note, self.last_position)
        if "slur_end" in token["note"]:
            if self.slur_start is None:
                raise ValueError("Slur end without start")
            self.active_scoreline.register("slur", start=self.slur_start, end=(note, self.last_position))
            self.slur_start = None
        
        multiplier = 1.5 if note.is_dotted else 1.
        space = self.active_duration_in_spaces * multiplier
        self.forward(space)
        
    def process_slur_if_present(self, note_token, note: Note = None, position: int = None):
        if note is None:
            note = Note.from_token(note_token)
            note.duration = self.active_duration
        
        position = position or self.last_position
        if "slur_start" in note_token:
            self.slur_start = (note, position)
        if "slur_end" in note_token:
            if self.slur_start is not None:
                self.active_scoreline.register("slur", start=self.slur_start, end=(note, position))
                self.slur_start = None
            else:
                raise ValueError("Slur end without start")