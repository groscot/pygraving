from pygraving.config import config
from pygraving.note import Note

from .commons import GenericLayout, PositionDegreeBounds


class AutoLayout(GenericLayout):
    """
    The origin is the left side of the center staff line
    """
    x: int = 0
    y: int = 0
    length: int = 650
    padding: int = 10
    
    #---
    
    min_degree = 0 -1 # bottom C
    max_degree = 12 +1 # top A
        
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
            #     max_position_offset += args["number"] * config.CLEF_ALTERATIONS_SPACE
            # elif what == "signature":
            #     max_position_offset += config.SIGNATURE_SPACE
        self.min_degree = bounds.min_degree
        self.max_degree = bounds.max_degree
        max_position = bounds.max_position #+ max_position_offset
        return max_position, max_position_type, bounds.min_degree, bounds.max_degree
    
    def run(self):
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
    