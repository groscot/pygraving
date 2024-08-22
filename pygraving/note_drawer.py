import os
import pathlib
from math import pi

import cairo

from .config import Config
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasCairoContext

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

class NoteDrawer(HasCairoContext):
    def get_note_ellipse_size(self):
        return (config("NOTE_ELLIPSE_BASE_WIDTH") /2,
                config("NOTE_ELLIPSE_BASE_HEIGHT") /2)
    
    def draw_centered_ellipse(self, hole=True, angled=True):
        if angled:
            self.ctx.rotate(config.NOTE_ANGLE)
        
        w, h = (config("NOTE_ELLIPSE_BASE_WIDTH") / 2, config("NOTE_ELLIPSE_BASE_HEIGHT") / 2)
        self.ctx.scale(w, h)
        self.ctx.arc(0, 0, 1, 0, 2*pi)
        self.ctx.fill()

        if hole:
            sx, sy = config.NOTE_HOLE_SCALE_X, config.NOTE_HOLE_SCALE_Y
            if not angled:
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
    
    def draw_stem(self, duration: int, up: bool = True):
        lw = config.STEM_LW
        
        x = config("NOTE_ELLIPSE_BASE_WIDTH") /2 - config.half(lw)
        sign = 1 if up else -1
        y_from = -sign * config("NOTE_STEM_Y_OFFSET")
        y_to   = -sign * config("STEM_LENGTH")

        self.ctx.move_to(x*sign, y_from)
        self.ctx.line_to(x*sign, y_to)
        self.stroke(lw)
        
        if duration >= 3:
            original_height = CURL_ORIGINAL_HEIGHT
            target_height = config("STEM_LENGTH")
            scale = target_height / original_height
            self.ctx.save()
            
            self.ctx.translate(x*sign, y_to)
            flip_y = 1 if up else -1
            self.ctx.scale(scale, scale*flip_y)
            draw_curl(self.ctx)
            self.ctx.restore()
    
    def draw_dot(self, x: int, y: int):
        radius = config("NOTE_DOT_RADIUS")
        self.ctx.arc(x, y, radius, 0, 2*pi)
        self.ctx.fill()
        
    def draw_at(self, x: int, y: int, duration: int,
                up: bool = True, beamed: bool = False,
                modifiers=""):
        self.ctx.save()
        self.ctx.translate(x, y)
        
        alteration_x_offset = config.STAFF_LINE_HEIGHT/2
        if duration >= 1 and not beamed:
            self.draw_stem(duration, up=up)
        if "#" in modifiers:
            self.draw_alteration("sharp", align="r", x_offset=alteration_x_offset)
        elif "b" in modifiers:
            self.draw_alteration("flat", align="r", x_offset=alteration_x_offset)
        elif "n" in modifiers:
            self.draw_alteration("natural", align="r", x_offset=alteration_x_offset)
        self.draw_centered_ellipse(hole = duration < 2, angled = duration >= 1)
        
        self.ctx.restore()
      