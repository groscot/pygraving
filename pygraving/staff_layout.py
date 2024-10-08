#===========
#! DEPRECATED
#! DEPRECATED
#! DEPRECATED
#===========

from .config import config
from .note import Note


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

class StaffLayout():
    """
    The origin is the left side of the center staff line
    """
    x: int = 0
    y: int = 0
    length: int = 650
    padding: int = 10
    
    #---
    
    has_voice_tracks: int = 0
    min_degree = 0 -1 # bottom C
    max_degree = 12 +1 # top A
    
    def __init__(self):
        self.registered = []
        self.staff_origin_position_base = config.STAFF_ORIGIN_POSITION_BASE
        
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
    
    def position_to_x(self, position):
        return self.x + config("NOTE_SPACE") * (position + self.staff_origin_position_base)
    
    def degree_to_y(self, degree: int):
        # this one takes as base the lower C note
        base = -6
        y = (base+degree)*config.STAFF_LINE_HEIGHT/2
        return self.y - y
    
    def offset_origin_position_base(self, offset):
        self.staff_origin_position_base += offset

    def register(self, what, **args):
        assert what in ["bar", "silence", "signature", "note", "chord", "beamed_group", "clef_alterations"]
        if what == "note":
            # print(args["note"].extras)
            if args["note"].extras.get("voice"):
                self.has_voice_tracks = max(self.has_voice_tracks, len(args["note"].extras.get("voice")))
        self.registered.append((what, args))
        
    def calculate_min_max_registered(self):
        # Remark: the +/-1 are to include the bottom/top edge of the notes (0 is their center)
        bounds = PositionDegreeBounds()
        max_position_type = None
        max_position_offset = 0
        for what, args in self.registered:
            if what == "bar":
                if args["position"] > bounds.max_position:
                    max_position_type = "bar_" + args["style"]
                bounds.add_position(args["position"])
            elif what == "silence":
                bounds.add_position(args["position"])
            elif what == "note":
                note = args["note"]
                up_sign = 1 if note.up else -1
                degree = note.degree
                degree_corrected_with_stem = degree + up_sign * 2 *(note.stem_length/config.STAFF_LINE_HEIGHT)
                
                if args["position"] > bounds.max_position:
                    max_position_type = what
                bounds.add_position(args["position"])
                bounds.add_degree(degree-1, degree+1)
                bounds.add_degree(degree_corrected_with_stem)
                
                if note.extras.get("fingering_string"):
                    bounds.add_degree(-2)
                if note.duration >= 3:
                    bounds.add_position(args["position"] + 0.3) # account for the curl
                if note.is_dotted:
                    bounds.add_position(args["position"] + config("DOT_X_OFFSET")/config("NOTE_SPACE"))
            elif what == "chord":
                for note_token in args["notes"]:
                    note = Note.from_token(note_token)
                    up_sign = 1 if args.get("up", True) else -1
                    degree = note.degree
                    degree_corrected_with_stem = degree + up_sign * 2 * (note.stem_length/config.STAFF_LINE_HEIGHT)
                    if args["position"] > bounds.max_position:
                        max_position_type = what
                    bounds.add_position(args["position"])
                    bounds.add_degree(degree-1, degree+1)
                    bounds.add_degree(degree_corrected_with_stem)
            elif what == "clef_alterations":
                degrees = self.generate_alterations_degrees(args["type"], args["number"])
                bounds.add_degree(max(degrees)+2) #i) +2 because the # is quite high
                max_position_offset += args["number"] * config.CLEF_ALTERATIONS_SPACE
            elif what == "signature":
                max_position_offset += config.SIGNATURE_SPACE
        self.min_degree = bounds.min_degree
        self.max_degree = bounds.max_degree
        max_position = bounds.max_position + max_position_offset
        return max_position, max_position_type, bounds.min_degree, bounds.max_degree
    
    def autolayout_from_registered(self):
        max_position, max_position_type, min_degree, max_degree = self.calculate_min_max_registered()
        
        # stem_length = config("STEM_LENGTH")
        min_y = self.degree_to_y(min_degree) + self.padding # + stem_length
        max_y = self.degree_to_y(max_degree) - self.padding # + stem_length
        height = int(min_y - max_y)
        
        self.x = self.padding
        self.y = self.padding + (max_degree - 6)*config.STAFF_LINE_HEIGHT/2 #  + stem_length
        
        if self.has_voice_tracks:
            height += self.has_voice_tracks * int(config("LYRICS_SPACE"))
        
        length = self.position_to_x(max_position)
        if max_position_type and max_position_type.startswith("bar"):
            style = max_position_type.split("_")[1].replace(":", "")
            if style == "|":
                length -= self.padding
            else:
                multiplier = 2 if style[1] == "|" else 3
                length -= self.padding - config.STAFF_LW*multiplier
        else:
            length += self.note_helper_line_padding(include_note=False)
        self.length = length
        return (int(length + 2*self.padding), height)
    