from .config import Config

config = Config()

class StaffLayout():
    """
    The origin is the left side of the center staff line
    """
    x: int = 0
    y: int = 0
    length: int = 650
    padding: int = 10
    
    #---
    
    has_voice: bool = False
    min_degree = 0 -1 # bottom C
    max_degree = 12 +1 # top A
    
    def __init__(self):
        self._registered = []
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
        delta_x = config.STAFF_LINE_HEIGTH * config.NOTE_SPACE * config.NOTE_HELPER_LINE_PADDING_COEFF
        if include_note:
            delta_x += config.STAFF_LINE_HEIGTH * 1/2
        return delta_x
    
    def position_to_x(self, position):
        return self.x + config.STAFF_LINE_HEIGTH * config.NOTE_SPACE * (position + self.staff_origin_position_base)
    
    def degree_to_y(self, degree: int):
        # this one takes as base the lower C note
        base = -6
        y = (base+degree)*config.STAFF_LINE_HEIGTH/2
        return self.y - y
    
    def offset_origin_position_base(self, offset):
        self.staff_origin_position_base += offset

    def register(self, what, **args):
        assert what in ["bar", "note", "chord", "beamed_group", "clef_alterations"]
        if "voice" in args:
            self.has_voice = True
        self._registered.append((what, args))
        
    def calculate_min_max_registered(self):
        # Remark: the +/-1 are to include the bottom/top edge of the notes (0 is their center)
        max_position = 0
        max_position_type = None
        max_position_offset = 0
        min_degree = self.min_degree
        max_degree = self.max_degree
        for what, args in self._registered:
            if what == "bar":
                if args["position"] > max_position:
                    max_position_type = what
                max_position = max(max_position, args["position"])
            elif what == "note":
                up_sign = 1 if args.get("up", True) else -1
                degree = args["degree"]
                degree_corrected_with_stem = degree + up_sign * (config.STEM_LENGTH*2)
                if args["position"] > max_position:
                    max_position_type = what
                max_position = max(max_position, args["position"])
                max_degree = max(max_degree, degree+1)
                min_degree = min(min_degree, degree-1)
                max_degree = max(max_degree, degree_corrected_with_stem)
                min_degree = min(min_degree, degree_corrected_with_stem)
            elif what == "beamed_group":
                degrees = args["degrees"]
                max_position = max(max_position, max(args["positions"]))
                max_degree = max(max_degree, max(degrees)+1)
                min_degree = min(min_degree, min(degrees)-1)
            elif what == "clef_alterations":
                degrees = self.generate_alterations_degrees(args["type"], args["number"])
                max_degree = max(self.max_degree, max(degrees)+2) #i) +2 because the # is quite high
                max_position_offset = args["number"] * config.CLEF_ALTERATIONS_SPACE
        self.min_degree = min_degree
        self.max_degree = max_degree
        max_position = max_position + max_position_offset
        return max_position, max_position_type, min_degree, max_degree
    
    def autolayout_from_registered(self):
        max_position, max_position_type, min_degree, max_degree = self.calculate_min_max_registered()
        
        # stem_length = config.STEM_LENGTH * config.STAFF_LINE_HEIGTH
        min_y = self.degree_to_y(min_degree) + self.padding # + stem_length
        max_y = self.degree_to_y(max_degree) - self.padding # + stem_length
        height = int(min_y - max_y)
        
        self.x = self.padding
        self.y = self.padding + (max_degree - 6)*config.STAFF_LINE_HEIGTH/2 #  + stem_length
        
        if self.has_voice:
            height += int(config.STAFF_LINE_HEIGTH * config.LYRICS_SPACE)
        
        length = self.position_to_x(max_position)
        if max_position_type == "bar":
            length -= self.padding - config.STAFF_LW
        else:
            length += self.note_helper_line_padding(include_note=False)
        self.length = length
        return (int(length + 2*self.padding), height)
    