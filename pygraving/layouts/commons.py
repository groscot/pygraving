from pygraving.config import config
from pygraving.note import Note


class PositionDegreeBounds():
    max_position = 0
    min_degree = 0 -1 # bottom C
    max_degree = 12 +1 # top A
    
    def add_position(self, position):
        self.max_position = max(self.max_position, position)
        
    def add_degree(self, degree_min, degree_max=None):
        degree_max = degree_max or degree_min
        self.min_degree = min(self.min_degree, degree_min)
        self.max_degree = max(self.max_degree, degree_max)
        
class GenericLayout():
    """
    The origin is the left side of the center staff line
    """
    x: int = 0
    y: int = 0
    length: int = 650
    has_voice_tracks: int = 0
    min_degree: int = -2
    
    def __init__(self):
        self.registered = []
        self.staff_origin_position_base = config("STAFF_ORIGIN_POSITION_BASE")
    
    @property
    def notes_start_x(self):
        return self.x + self.staff_origin_position_base
    
    def offset_origin_position_base(self, offset):
        self.staff_origin_position_base += offset
            
    def generate_alterations_degrees(self, type: str, number: int) -> list[int]:
        if type == "flat":
            min_d = 3
            d = 6
            skip = 3
        if type == "sharp":
            min_d = 7
            d = 10
            skip = 4
        
        degrees = []
        for i in range(number):
            degrees.append(d)
            d = (d-min_d + skip)%7 + min_d
        return degrees
    
    def note_helper_line_padding(self, include_note=True):
        delta_x = config("NOTE_SPACE") * config.NOTE_HELPER_LINE_PADDING_COEFF
        if include_note:
            delta_x += config.STAFF_LINE_HEIGHT * 1/2
        return delta_x
    
    def position_to_x(self, position: float) -> float:
        return self.notes_start_x + config("NOTE_SPACE") * position
    
    def degree_to_y(self, degree: int):
        # degree 0 = lower C note
        base = -6
        y = (base+degree)*config.STAFF_LINE_HEIGHT/2
        return self.y - y

    def register(self, what, **args):
        assert what in ["bar", "silence", "signature", "note", "chord", "beamed_group", "clef_alterations"]
        if what == "note":
            if args["note"].extras.get("voice"):
                self.has_voice_tracks = max(self.has_voice_tracks, len(args["note"].extras.get("voice")))
        self.registered.append((what, args))