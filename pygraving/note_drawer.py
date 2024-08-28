import os
import pathlib
from math import pi

import cairo

from .config import Config
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasParentCairoContext
from .note import Note

config = Config()

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
draw_curl = svg_path_to_ctx_fill( current_path / "shapes/curl.txt" )
draw_sharp = svg_path_to_ctx_fill( current_path / "shapes/sharp.txt" )
draw_flat = svg_path_to_ctx_fill( current_path / "shapes/flat.txt" )
draw_natural = svg_path_to_ctx_fill( current_path / "shapes/natural.txt" )

CURL_ORIGINAL_HEIGHT = 74
ALTERATION_ORIGINAL_HEIGHT = {
    "sharp": 24,
    "flat": 24,
    "natural": 24
}
ALTERATION_RELATIVE_VERTICAL_SHIFT = {
    "sharp": 0.0,
    "flat": 0.0,
    "natural": 0.0
}
DRAW_ALTERATION = {
    "sharp": draw_sharp,
    "flat": draw_flat,
    "natural": draw_natural
}

def resolve_align(width: float, align: str) -> float:
    if align == "c":
        return -width/2
    if align == "l":
        return width
    else:
        return -width


class NoteDrawer(HasParentCairoContext):
    def draw_centered_ellipse(self, note: Note):
        w, h = (config("NOTE_ELLIPSE_BASE_WIDTH") / 2, config("NOTE_ELLIPSE_BASE_HEIGHT") / 2)
        
        if note.is_opposite_x:
            self.ctx.translate(config("NOTE_ELLIPSE_BASE_WIDTH") - config.STEM_LW, 0)
        if note.is_angled:
            self.ctx.rotate(config.NOTE_ANGLE)
        self.ctx.scale(w, h)
        
        self.ctx.arc(0, 0, 1, 0, 2*pi)
        self.ctx.fill()

        if note.has_hole:
            sx, sy = config.NOTE_HOLE_SCALE_X, config.NOTE_HOLE_SCALE_Y
            if not note.is_angled:
                self.ctx.rotate(config.NOTE_ANGLE/2)
                sx, sy = sy, sx
            self.ctx.scale(sx, sy)
            self.ctx.arc(0, 0, 1, 0, 2*pi)
            self.ctx.set_operator(cairo.Operator.CLEAR)
            self.ctx.fill()
            self.ctx.set_operator(cairo.Operator.OVER)
    
    def draw_alteration(self, which="sharp", align: str = "r", x_offset: float = 0):
        scale = config.STAFF_LINE_HEIGHT/ALTERATION_ORIGINAL_HEIGHT[which]
        t_x = resolve_align(config("NOTE_ELLIPSE_BASE_WIDTH") + x_offset, align)
        self.ctx.save()
        self.ctx.translate(t_x, ALTERATION_RELATIVE_VERTICAL_SHIFT[which]*scale)
        self.ctx.scale(scale, scale)
        DRAW_ALTERATION[which](self.ctx)
        self.ctx.restore()
    
    def draw_stem(self, note: Note):
        x, y_from, y_to, sign = note.compute_one_stem_endpoints()

        self.ctx.move_to(x, y_from)
        self.ctx.line_to(x, y_to)
        self.stroke(config.STEM_LW)
        
        if note.duration >= 3:
            self.draw_curl_on_stem(x*sign, y_to, note)
    
    def draw_stem_for_chord(self, position: float, notes: list[Note], duration: int = 2, up: bool = True):
        x0 = self.parent.layout.position_to_x(position)
        stems = []
        for note in notes:
            x, y_from, y_to, sign = note.compute_one_stem_endpoints(x0=x0, y0=self.parent.layout.degree_to_y(note.degree))
            stems.append((x, y_from, y_to, sign))
        
        # find extremal values for y
        if up:
            y_min = max([y_from for _, y_from, _, _ in stems])
            y_max = min([y_to for _, _, y_to, _ in stems])
        else:
            y_min = min([y_from for _, y_from, _, _ in stems])
            y_max = max([y_to for _, _, y_to, _ in stems])
        y_tip = y_max

        self.ctx.move_to(x, y_max)
        self.ctx.line_to(x, y_min)
        self.stroke(config.STEM_LW)
        
        if duration >= 3:
            self.draw_curl_on_stem(x, y_tip, note)
    
    def draw_curl_on_stem(self, x: float, y: float, note: Note):
        original_height = CURL_ORIGINAL_HEIGHT
        target_height = note.stem_length
        scale = target_height / original_height
        self.ctx.save()
        
        self.ctx.translate(x, y)
        flip_y = 1 if note.up else -1
        self.ctx.scale(scale, scale*flip_y)
        draw_curl(self.ctx)
        self.ctx.restore()
        
    def draw_at(self, x: int, y: int, note: Note):
        self.ctx.save()
        self.ctx.translate(x, y)
        
        alteration_x_offset = config.STAFF_LINE_HEIGHT/2
        if note.has_stem:
            self.draw_stem(note)
        
        alteration = note.get_alteration()
        if alteration:
            self.parent.symbolDrawer.draw_alteration(alteration, align="r", x_offset=alteration_x_offset)
        
        self.draw_centered_ellipse(note)
        
        self.ctx.restore()