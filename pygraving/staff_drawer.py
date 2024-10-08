import os
import pathlib
from math import pi

from .beamed_group import BeamedGroup
from .config import config
from .layouts.auto import AutoLayout
from .layouts.justified import JustifiedLayout
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasCairoContext
from .note import Note
from .note_drawer import NoteDrawer
from .symbol_drawer import SymbolDrawer

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
draw_clef = svg_path_to_ctx_fill( current_path / "shapes/clef_G.txt" )

CLEF_ORIGINAL_HEIGHT = 1000

class StaffDrawer(HasCairoContext):
    _last_lyric_data = {0: None}
    in_group_after: bool = False
    has_clef_alterations: bool = False
    has_signature: bool = False
    clef: str = "clef_G"
    
    def init(self):
        self.layout = AutoLayout()
        # self.layout = JustifiedLayout()
        self.noteDrawer = NoteDrawer(self)
        self.beamedGroupHandler = BeamedGroup(self)
        self.symbolDrawer = SymbolDrawer(self)
        self.symbolDrawer.init()
    
    @property
    def bottom_staff_y(self):
        return self.layout.y + 2*config.STAFF_LINE_HEIGHT
    
    @property
    def top_staff_y(self):
        return self.layout.y - 2*config.STAFF_LINE_HEIGHT
    
    @property
    def x(self):
        return self.layout.x
    
    def draw_lines(self):
        for i in range(-2, 5-2):
            self.ctx.move_to(self.layout.x, self.layout.y - i*config.STAFF_LINE_HEIGHT)
            self.ctx.line_to(self.layout.x + self.layout.length, self.layout.y - i*config.STAFF_LINE_HEIGHT)
            self.stroke(config.STAFF_LW)
            
    def draw_left_line(self):
        delta_x = config.STAFF_LW/2 # to have perfect corners
        self.ctx.move_to(self.layout.x+delta_x, self.layout.y + 2*config.STAFF_LINE_HEIGHT)
        self.ctx.line_to(self.layout.x+delta_x, self.layout.y - 2*config.STAFF_LINE_HEIGHT)
        self.stroke(config.STAFF_LW)
    
    def draw_clef(self):
        if self.clef == 'clef_G':
            self.symbolDrawer.draw("clef_G", degree=13, x_offset=self.layout.x +config("CLEF_LEFT_MARGIN"), y_offset=0.15*config.STAFF_LINE_HEIGHT)
        if self.clef == 'clef_F':
            self.symbolDrawer.draw("clef_F", degree=8, x_offset=self.layout.x +config("CLEF_LEFT_MARGIN"))
        
    def config_clef_alterations(self, type: str, number: int):
        self.layout.offset_origin_position_base(config("CLEF_ALTERATIONS_SPACE")*number)
        self.has_clef_alterations = True
    
    def place_clef_alterations(self, type: str, number: int):
        offset = config("CLEF_ALTERATIONS_SPACE")*number
        if self.has_signature:
            offset += config("SIGNATURE_SPACE")*0.75
        degrees = self.layout.generate_alterations_degrees(type, number)
        for i, degree in enumerate(degrees):
            self.draw_clef_alteration(type, config("CLEF_ALTERATIONS_SPACE")*i - offset, degree)
        
    def place_note_helper_lines(self, position, from_degree, to_degree, x_offset = 0):
        _from = min(from_degree, to_degree)
        _to = max(from_degree, to_degree)
        x = self.layout.position_to_x(position) + x_offset
        delta_x = self.layout.note_helper_line_padding()
        for degree in range(_from, _to+1):
            if degree%2 == 1:
                continue
            y = self.layout.degree_to_y(degree)
            self.ctx.move_to(x - delta_x, y)
            self.ctx.line_to(x + delta_x, y)
            self.stroke(config.STAFF_LW)
    
    def draw_clef_alteration(self, type: str, position: float, degree: int):
        x = self.layout.notes_start_x + position
        y = self.layout.degree_to_y(degree)
        
        self.ctx.save()
        self.ctx.translate(x, y)
        self.noteDrawer.draw_alteration(which=type, align="r", x_offset=0)
        self.ctx.restore()
    
    def draw_bar(self, x: int, lw_multiplier: float = 1.0):
        lw = config.STAFF_LW * lw_multiplier
        delta_x = 0 #lw/2 # to have a centered line
        self.ctx.move_to(x - delta_x, self.layout.y + 2*config.STAFF_LINE_HEIGHT)
        self.ctx.line_to(x - delta_x, self.layout.y - 2*config.STAFF_LINE_HEIGHT)
        self.stroke(lw)
    
    def place_bar(self, position: int, style: str = "|"):
        x = self.layout.position_to_x(position)
        draw_dots = False
        if ":" in style:
            delta_sign = -1 if style[0] == ":" else 1
            draw_dots = True
            style = style.replace(":", "")
        
        if style == "|":
            self.draw_bar(x, lw_multiplier=1.0)
        elif style == "||" or style == "[|" or style == "|]":
            left_thickness = 3.0 if style[0] == "[" else 1.0
            right_thickness = 3.0 if style[1] == "]" else 1.0
            delta_x = config.STAFF_LW * 2
            self.draw_bar(x - delta_x, lw_multiplier=left_thickness)
            self.draw_bar(x + delta_x, lw_multiplier=right_thickness)
        
        if draw_dots:
            delta_x = config.STAFF_LW * 4 + 2 * config("NOTE_DOT_RADIUS")
            y1 = self.layout.degree_to_y(5)
            y2 = self.layout.degree_to_y(7)
            self.symbolDrawer.draw_dot(x + delta_x * delta_sign, y1)
            self.symbolDrawer.draw_dot(x + delta_x * delta_sign, y2)
    
    def config_signature(self, digit_1: int = 1, digit_2: int = 1, is_C: bool = False):
        space = config("SIGNATURE_SPACE")
        self.layout.offset_origin_position_base(space*0.75)
        self.has_signature = True
        
    def place_signature(self, digit_1: int = 1, digit_2: int = 1, is_C: bool = False):
        space = config("SIGNATURE_SPACE")
        offset = space*0.75
        x = self.layout.notes_start_x - offset - space/4
        self.ctx.translate(x, 0)
        if is_C:
            self.symbolDrawer.draw_signature_C()
        else:
            self.symbolDrawer.draw_signature_digits(digit_1, digit_2)
        self.ctx.translate(-x, 0)
        
    def place_silence(self, position: int, duration: int):
        type = ["whole", "half", "quarter", "eighth", "sixt"][duration]
        self.symbolDrawer.draw_silence(type, position=position)
    
    def place_note(
        self, position: int, note: Note
    ):
        # get from extras for voice voice_duration hyphen_before
        voice = note.extras.get("voice", None)
        voice_duration = note.extras.get("voice_duration", None)
        hyphen_before = note.extras.get("hyphen_before", False)
        
        x = self.layout.position_to_x(position)
        y = self.layout.degree_to_y(note.degree)
        
        self.noteDrawer.draw_at(x, y, note)
        
        helper_line_x_offset = 0
        if note.is_opposite_x:
            helper_line_x_offset = config("NOTE_ELLIPSE_BASE_WIDTH") - config.STEM_LW
        if note.degree <= 0:
            self.place_note_helper_lines(position, note.degree, 0, helper_line_x_offset)
        if note.degree >= 12:
            self.place_note_helper_lines(position, 12, note.degree, helper_line_x_offset)
        
        if voice is not None and len(voice) > 0:
            voice_duration = voice_duration or note.duration
            track_i = 0
            for track, hyphen in zip(voice, hyphen_before):
                self.place_voice(track_i, position, note.duration, voice_duration, track, hyphen)
                track_i += 1

    def config_beamed_group(self, position: float, notes: list[dict], duration: int, up: bool = True):
        self.beamedGroupHandler.init(position, notes, duration, up)
        notes = self.beamedGroupHandler.get_notes_for_registration()
        for position, note in notes:
            self.register("note", position=position, note=note)

    def place_beamed_group(self, notes: list[dict], duration: int, position: float, up: bool = True):
        self.beamedGroupHandler.init(position, notes, duration, up)
        self.beamedGroupHandler.draw_beam()
        self.beamedGroupHandler.draw_stems()
    
    def place_chord(self, notes: list[dict], duration: int, position: float, up: bool = True):
        degrees = []
        note_objects = []
        
        for _note in notes:
            params = Note.parse_note_token(_note)
            note = Note(**params | {"duration": duration})
            if not up:
                note.modifiers += "!"
            note._has_stem = False
            degrees.append(note.degree)
            note_objects.append(note)
            
        self.noteDrawer.draw_stem_for_chord(position, note_objects, duration, up)
        
        order_indices, sorted_degrees = zip(*sorted(enumerate(degrees), key=lambda x: x[1]))
        
        # find if in sorted degrees list, there is a number directly +1 from the previous one
        is_consecutive = []
        is_flipped_list = [False]
        for i in range(len(sorted_degrees)-1):
            is_consecutive = sorted_degrees[i+1] - sorted_degrees[i] == 1
            is_flipped_list.append(is_consecutive and not is_flipped_list[-1])
        
        is_flipped_list = [is_flipped_list[i] for i in order_indices] # reapply the order_indices
        for note, is_flipped in zip(note_objects, is_flipped_list):
            note.is_opposite_x = is_flipped
            self.place_note( position, note )
        

    def place_voice(self, track_i: int, position: int, note_duration: int, voice_duration: int, voice: str, hyphen_before=False):
        if hyphen_before and self._last_lyric_data[track_i] is None:
            raise ValueError("Cannot place hyphen before first lyric")
        
        x = self.layout.position_to_x(position)
        y = self.layout.degree_to_y(self.layout.min_degree) + config("LYRICS_SPACE")*(track_i + 1)
        self.ctx.select_font_face(config.VOICE_FONT_FACE)
        self.ctx.set_font_size(config.VOICE_FONT_SIZE)
        
        # compute optical length of text to center it
        width = self.ctx.text_extents(voice)[2]
        start = x-width/2
        self.ctx.move_to(start, y)
        self.ctx.show_text(voice)
        
        if hyphen_before:
            hyphen_length = self.ctx.text_extents("-")[2]
            x = (self._last_lyric_data[track_i] + start)/2 - hyphen_length/2
            self.ctx.move_to(x, y)
            self.ctx.show_text("-")
        self._last_lyric_data[track_i] = start+width

    def place_slur(self, start: tuple[Note, float], end: tuple[Note, float]):
        start_x = self.layout.position_to_x(start[1])
        end_x = self.layout.position_to_x(end[1])
        direction = 1 if start[0].up else -1
        self.symbolDrawer.draw_slur(start_x, start[0].degree, end_x, end[0].degree, direction)
    
    def register(self, what, **args):
        self.layout.register(what, **args)
        if hasattr(self, "config_" + what):
            getattr(self, "config_" + what)(**args)

    def place_registered(self):
        for what, args in self.layout.registered:
            getattr(self, "place_" + what)(**args)