from .config import Config

config = Config()

NOTE_DEGREES = ["do", "re", "mi", "fa", "sol", "la", "si"]

class Note:
    def __init__(
        self,
        degree: int, duration: int = 2, beamed: bool = False, modifiers: str = "", is_opposite_x: bool = False,
        stem_length: float = config("STEM_LENGTH"),
        **kwargs
    ):
        self.degree = Note.parse_degree(degree)
        self.duration = duration
        self.beamed = beamed
        self.modifiers = modifiers
        self.stem_length = stem_length
        self.is_opposite_x = is_opposite_x
        self._has_stem = True
        self.extras = {key: val for key, val in kwargs.items() if not hasattr(self, key)}

    @classmethod
    def parse_degree(cls, degree: int|str) -> int:
        if isinstance(degree, str):
            print("DE", degree)
            # count number of "+" and "-" in the string
            pluses = degree.count("+")
            minuses = degree.count("-")
            degree = degree.replace("+", "").replace("-", "")
            return NOTE_DEGREES.index(degree) + (pluses - minuses)*7
        return degree

    @property
    def has_stem(self):
        return self._has_stem and self.duration >= 1 and not self.beamed

    @property
    def has_hole(self):
        if self.beamed:
            return False
        return self.duration < 2

    @property
    def is_angled(self):
        return self.duration >= 1

    @property
    def is_dotted(self):
        return "." in self.modifiers

    @property
    def up(self):
        return "!" not in self.modifiers

    def get_alteration(self):
        if "#" in self.modifiers:
            return "sharp"
        elif "b" in self.modifiers:
            return "flat"
        elif "n" in self.modifiers:
            return "natural"
        return None

    @classmethod
    def from_token(cls, token):
        return cls(**cls.parse_note_token(token))

    @classmethod
    def parse_note_token(cls, token):
        modifiers = ""
        if "dotted" in token:
            modifiers += "."
        if "flipped" in token:
            modifiers += "!"
        if "alteration" in token:
            modifiers += token["alteration"]
        
        if "voice" not in token:
            return dict(degree=token["degree"], modifiers=modifiers)
        else:
            voice = token["voice"]
            hyphen_before = "hyphen" in token
            if hyphen_before:
                voice = voice[1]
            else:
                voice = voice[0]
            return dict(
                degree=token["degree"], modifiers=modifiers, voice=voice, hyphen_before=hyphen_before
            )
    
    def compute_one_stem_endpoints(self, x0: float = 0.0, y0: float = 0.0):
        x = config("NOTE_ELLIPSE_BASE_WIDTH") / 2 - config.half(config.STEM_LW)
        sign = 1 if self.up else -1
        y_from = -sign * config("NOTE_STEM_Y_OFFSET")
        y_to   = -sign * self.stem_length
        
        return (x0 + x*sign, y0 + y_from, y0 + y_to, sign)
