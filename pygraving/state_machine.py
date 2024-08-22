# from enum import Enum

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
        return 4/(2**self.active_duration)
    
    def forward(self, amount: int = None):
        amount = amount or self.active_duration_in_spaces
        self.last_position += amount
    
    def backward(self, amount: int = None):
        amount = amount or self.active_duration_in_spaces
        self.last_position -= amount
    
    def run(self, parsed_tokens: list):
        for token in parsed_tokens:
            self.process_token(token)
    
    def write_note(self, degree: str, modifiers: str = ""):
        self.active_scoreline.register(
            "note", position=self.last_position, degree=int(degree), duration=self.active_duration, modifiers=modifiers
        )
    
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
        if "note" in token:
            self.process_note(token)
            return
        if "chord" in token:
            # print([n for n in _token.chord.notes])
            # for note in token["chord"]:
            #     self.process_note(note)
            # self.forward()
            for degree in token["chord"]["notes"]:
                self.write_note(degree=degree)
            self.forward()
            return
        if "beam" in token:
            N = len(token["beam"]["notes"])
            positions = [self.last_position+i for i in range(N)]
            self.active_scoreline.register(
                "beamed_group", positions=positions, degrees=[int(note) for note in token["beam"]["notes"]], duration=1
            )
            self.forward(N)
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
        modifiers = ""
        if "dotted" in token["note"]:
            modifiers += "."
        if "alteration" in token["note"]:
            modifiers += token["note"]["alteration"]
        if "voice" not in token["note"]:
            self.write_note(degree=token["note"]["degree"], modifiers=modifiers)
        else:
            voice = token["note"]["voice"]
            hyphen_before = "hyphen" in token["note"]
            if hyphen_before:
                voice = voice[1]
            else:
                voice = voice[0]
            self.active_scoreline.register(
                "note", position=self.last_position, degree=int(token["note"]["degree"]), duration=self.active_duration,
                voice=voice, hyphen_before=hyphen_before
            )
        self.forward()