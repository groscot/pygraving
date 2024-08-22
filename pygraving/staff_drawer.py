import os
import pathlib

from .beamed_group import BeamedGroup
from .config import Config
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasCairoContext
from .note_drawer import NoteDrawer
from .staff_layout import StaffLayout

config = Config()

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
draw_clef = svg_path_to_ctx_fill( current_path / "shapes/F_clef.txt" )

CLEF_ORIGINAL_HEIGHT = 1000

class StaffDrawer(HasCairoContext):
    _last_lyric_data = None
    
    def init(self):
        self.layout = StaffLayout()
        self.noteDrawer = NoteDrawer(self.ctx)
        self.beamedGroupHandler = BeamedGroup(self.ctx)
    
    def draw_lines(self):
        for i in range(-2, 5-2):
            self.ctx.move_to(self.layout.x, self.layout.y - i*config.STAFF_LINE_HEIGTH)
            self.ctx.line_to(self.layout.x + self.layout.length, self.layout.y - i*config.STAFF_LINE_HEIGTH)
            self.stroke(config.STAFF_LW)
            
    def draw_left_line(self):
        delta_x = config.STAFF_LW/2 # to have perfect corners
        self.ctx.move_to(self.layout.x+delta_x, self.layout.y + 2*config.STAFF_LINE_HEIGTH)
        self.ctx.line_to(self.layout.x+delta_x, self.layout.y - 2*config.STAFF_LINE_HEIGTH)
        self.stroke(config.STAFF_LW)
    
    def draw_clef(self):
        # Compute scale and position
        original_height = CLEF_ORIGINAL_HEIGHT
        target_height = config.STAFF_LINE_HEIGTH * 7.
        offset = target_height * 1.65 / 7.
        scale = target_height / original_height
        x = self.layout.x + config.STAFF_LINE_HEIGTH * config.NOTE_SPACE/8
        y = self.layout.y - target_height + offset + 2*config.STAFF_LINE_HEIGTH
        
        # Draw
        self.ctx.save()
        self.ctx.translate(x, y)
        self.ctx.scale(scale, scale)
        draw_clef(self.ctx)
        self.ctx.restore()
        
    def place_clef_alterations(self, type: str, number: int):
        degrees = self.layout.generate_alterations_degrees(type, number)
        for i, degree in enumerate(degrees):
            self.draw_clef_alteration(type, config.CLEF_ALTERATIONS_SPACE*i, degree)
        self.layout.offset_origin_position_base(config.CLEF_ALTERATIONS_SPACE*number)
        
    def place_note_helper_lines(self, position, from_degree, to_degree):
        _from = min(from_degree, to_degree)
        _to = max(from_degree, to_degree)
        x = self.layout.position_to_x(position)
        delta_x = self.layout.note_helper_line_padding()
        for degree in range(_from, _to+1):
            if degree%2 == 1:
                continue
            y = self.layout.degree_to_y(degree)
            self.ctx.move_to(x - delta_x, y)
            self.ctx.line_to(x + delta_x, y)
            self.stroke(config.STAFF_LW)
    
    def draw_clef_alteration(self, type: str, position: int, degree: int):
        x = self.layout.position_to_x(position)
        y = self.layout.degree_to_y(degree)
        
        self.ctx.save()
        self.ctx.translate(x, y)
        self.noteDrawer.draw_alteration(which=type, align="r", x_offset=0)
        self.ctx.restore()
    
    def draw_bar(self, x: int, lw_multiplier: float = 1.0):
        lw = config.STAFF_LW * lw_multiplier
        delta_x = lw/2 # to have a centered line
        self.ctx.move_to(x - delta_x, self.layout.y + 2*config.STAFF_LINE_HEIGTH)
        self.ctx.line_to(x - delta_x, self.layout.y - 2*config.STAFF_LINE_HEIGTH)
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
        elif style == "||":
            delta_x = config.STAFF_LW * 2
            self.draw_bar(x - delta_x, lw_multiplier=1.0)
            self.draw_bar(x + delta_x, lw_multiplier=1.0)
        
        if draw_dots:
            delta_x = config.STAFF_LW * 4 + 2 * config.NOTE_DOT_RADIUS* config.STAFF_LINE_HEIGTH
            y1 = self.layout.degree_to_y(5)
            y2 = self.layout.degree_to_y(7)
            self.noteDrawer.draw_dot(x + delta_x * delta_sign, y1)
            self.noteDrawer.draw_dot(x + delta_x * delta_sign, y2)
        
    def place_dot(self, position: int, degree: int):
        x = self.layout.position_to_x(position)
        y = self.layout.degree_to_y(degree)
        
        x += config.STAFF_LINE_HEIGTH/2 * config.NOTE_ELLIPSE_BASE_WIDTH + config.DOT_X_OFFSET * config.STAFF_LINE_HEIGTH
        if (2 <= degree <= 10) and (degree%2 == 0):
            y += config.DOT_Y_OFFSET * config.STAFF_LINE_HEIGTH
        self.noteDrawer.draw_dot(x, y)
    
    def place_note(
        self, position: int, degree: int, duration: int,
        up: bool = True, beamed: bool = False, modifiers="",
        voice: str|None = None, voice_duration: int|None = None, hyphen_before=False
    ):
        x = self.layout.position_to_x(position)
        y = self.layout.degree_to_y(degree)
        
        self.noteDrawer.draw_at(x, y, duration, up, beamed, modifiers)
        if "." in modifiers:
            self.place_dot(position, degree)
        
        if degree <= 0:
            self.place_note_helper_lines(position, degree, 0)
        if degree >= 12:
            self.place_note_helper_lines(position, 12, degree)
        
        if voice is not None:
            voice_duration = voice_duration or duration
            self.place_voice(position, duration, voice_duration, voice, hyphen_before)
            
    def place_beamed_group(self, positions: list[int], degrees: list[int], duration: int, up: bool = True):
        notes = []
        for pos, degree in zip(positions, degrees):
            notes.append((self.layout.position_to_x(pos), self.layout.degree_to_y(degree)))
            self.place_note(pos, degree, duration=4, up=up, beamed=True)
        self.beamedGroupHandler.register_notes(notes, duration, up)
        self.beamedGroupHandler.draw_beam()
        self.beamedGroupHandler.draw_stems()

    def place_voice(self, position: int, note_duration: int, voice_duration: int, voice: str, hyphen_before=False):
        if hyphen_before and self._last_lyric_data is None:
            raise ValueError("Cannot place hyphen before first lyric")
        
        x = self.layout.position_to_x(position)
        y = self.layout.degree_to_y(self.layout.min_degree) + config.STAFF_LINE_HEIGTH * config.LYRICS_SPACE
        self.ctx.select_font_face(config.VOICE_FONT_FACE)
        self.ctx.set_font_size(config.VOICE_FONT_SIZE)
        
        # compute optical length of text to center it
        width = self.ctx.text_extents(voice)[2]
        start = x-width/2
        
        self.ctx.move_to(start, y)
        self.ctx.show_text(voice)
        
        if hyphen_before:
            hyphen_length = self.ctx.text_extents("-")[2]
            x = (self._last_lyric_data + start)/2 - hyphen_length/2
            self.ctx.move_to(x, y)
            self.ctx.show_text("-")
        self._last_lyric_data = start+width

    def register(self, what, **args):
        self.layout.register(what, **args)

    def place_registered(self):
        for what, args in self.layout._registered:
            getattr(self, "place_" + what)(**args)