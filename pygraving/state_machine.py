# from enum import Enum

from .note import Note
from .parser import parse_input
from .score import Score

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
        score = Score()
        self.score = score
        self.active_duration = 2
        self.active_scoreline = None
        self.last_position = 0 #! WARNING will be problematic if multiple lines and switching between them
    
    def __call__(self, text_input: str):
        parsed_tokens = parse_input(text_input)
        self.run(parsed_tokens)
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
            self.forward()
            return
        if "beam" in token:
            self.active_scoreline.register(
                "beamed_group", notes=token["beam"]["notes"], duration=1, position=self.last_position, up="flipped" not in token["beam"],
            )
            self.forward( len(token["beam"]["notes"]) )
            return
        
    def process_command(self, token):
        if token["command"] == "BEGIN":
            if token["object"] == "line":
                self.active_scoreline = self.score.add_scoreline()
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
        else:
            raise ValueError("Unknown command: " + token["command"])
        
    def process_note(self, token):
        note = Note.from_token(token["note"])
        note.duration = self.active_duration
        self.active_scoreline.register("note", note=note, position=self.last_position)
        self.forward()