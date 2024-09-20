from .config import config

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
        self.selection = {}
        self._has_stem = True
        self.extras = {key: val for key, val in kwargs.items() if not hasattr(self, key)}

    @classmethod
    def parse_degree(cls, degree: int|str) -> int:
        if isinstance(degree, str):
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

    def selection_translation(self, key, value):
        return self.selection.get(key, {}).get(value, 0) * config.STAFF_LINE_HEIGHT

    @classmethod
    def from_token(cls, token):
        return cls(**cls.parse_note_token(token))

    @classmethod
    def parse_note_token(cls, token):
        modifiers = ""
        fingering_finger = None
        fingering_string = None
        duration = 2
        if "duration" in token:
            duration = token["duration"]
            if isinstance(duration, list):
                duration = duration[0]
            duration = int(duration)
        
        if "fingering_finger" in token:
            fingering_finger = int(token["fingering_finger"][0])
        if "fingering_string" in token:
            fingering_string = int(token["fingering_string"][0])
        
        if "dotted" in token:
            modifiers += "."
        if "flipped" in token:
            modifiers += "!"
        if "alteration" in token:
            modifiers += token["alteration"]
        
        if "voice" not in token:
            return dict(
                duration=duration,
                degree=token["degree"],
                modifiers=modifiers,
                fingering_finger=fingering_finger,
                fingering_string=fingering_string
            )
        else:
            voice = token["voice"]
            hyphen_before = []
            tracks = []
            for track in voice:
                has_voice = track.startswith("-")
                hyphen_before.append(has_voice)
                if has_voice:
                    track = track[1:]
                tracks.append(track)
            return dict(
                duration=duration,
                degree=token["degree"], modifiers=modifiers,
                fingering_finger=fingering_finger, fingering_string=fingering_string,
                voice=tracks, hyphen_before=hyphen_before
            )
    
    def compute_one_stem_endpoints(self, x0: float = 0.0, y0: float = 0.0):
        x = config("NOTE_ELLIPSE_BASE_WIDTH") / 2 - config.half(config.STEM_LW)
        sign = 1 if self.up else -1
        y_from = -sign * config("NOTE_STEM_Y_OFFSET")
        y_to   = -sign * self.stem_length
        
        return (x0 + x*sign, y0 + y_from, y0 + y_to, sign)
