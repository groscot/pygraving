import os
import pathlib
from math import pi

import cairo

from .config import config
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasParentCairoContext
from .note import Note

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

ALTERATION_SYMBOLS_TO_NAME = {
    "#": "sharp",
    "b": "flat",
    "n": "natural",
    ".":  "dotted",
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
    
    def draw_fingering(self, x: float, degree: int, fingering: int, circled: bool):
        if circled:
            degree = -2
        else:
            degree = degree + 0.66 # 2/3 to prevent perfect alignment with grid (a.k.a. "collision")
        y = self.parent.layout.degree_to_y(degree) 
        
        self.ctx.save()
        self.ctx.select_font_face(config.FINGERING_FONT_FACE)
        self.ctx.set_font_size(config("FINGERING_RELATIVE_FONT_SIZE"))
        # width = self.ctx.text_extents(str(fingering))[2]
        text_extents = self.ctx.text_extents(str(fingering))
        width = text_extents[2]
        height = text_extents[3]
        x -= width/2
        
        if not circled:
            x -= config("NOTE_ELLIPSE_BASE_WIDTH")
        
        self.ctx.move_to(x, y)
        self.ctx.show_text(str(fingering))
        self.ctx.new_path()
        
        if circled:
            self.ctx.set_line_width(config.FINGERING_LW)
            radius = config("FINGERING_RELATIVE_FONT_SIZE")/2
            self.ctx.arc(x + width/2, y - height/2, radius, 0, 2*pi)
            self.ctx.stroke()
        self.ctx.restore()
    
    def draw_at(self, x: int, y: int, note: Note):
        self.ctx.save()
        self.ctx.translate(x, y)
        
        alteration_x_offset = config.STAFF_LINE_HEIGHT/2
        if note.has_stem:
            self.draw_stem(note)
        
        # selection = note.get_active_selection()
        selection = note.selection
        
        # get_active_selection(self):
        # if "modifier" in self.selection:
        #     return ALTERATION_SYMBOLS_TO_NAME.get(self.selection["modifier"].get("value", ""), None)
        # if self.selection.get("target_type", "") == "fingering_finger":
        #     return "fingering_finger"
        # if self.selection.get("target_type", "") == "fingering_string":
        #     return "fingering_string"
        # return None
        
        alteration = note.get_alteration()
        if alteration:
            selected_alteration = "modifier" in selection and \
                ALTERATION_SYMBOLS_TO_NAME[selection["modifier"]["value"]] == alteration
            is_special_color = config.show_debug("show_selected_object") and selected_alteration
            with self.conditional_translation(selected_alteration, note.selection_translation("modifier", "x"), note.selection_translation("modifier", "y")):
                with self.conditional_color(is_special_color, 0,0,1):
                    self.parent.symbolDrawer.draw_alteration(alteration, align="r", x_offset=alteration_x_offset)
        
        if note.is_dotted:
            x_dot = config("NOTE_ELLIPSE_BASE_WIDTH") / 2 + config("DOT_X_OFFSET")
            y_dot = 0
            if (2 <= note.degree <= 10) and (note.degree%2 == 0):
                y_dot += config("DOT_Y_OFFSET")
            is_special_color = config.show_debug("show_selected_object") and "dot" in selection
            with self.conditional_translation("dot" in selection, note.selection_translation("dot", "x"), note.selection_translation("dot", "y")):
                with self.conditional_color(is_special_color, 0,0,1):
                    self.parent.symbolDrawer.draw_dot(x_dot, y_dot)
        
        self.draw_centered_ellipse(note)
        self.ctx.restore()
        
        #i) placed after ctx.restore() because the methods apply transformations
        
        fingering_finger = note.extras.get("fingering_finger", None)
        if fingering_finger is not None:
            is_special_color = config.show_debug("show_selected_object") and "fingering_finger" in selection
            with self.conditional_translation("fingering_finger" in selection, note.selection_translation("fingering_finger", "x"), note.selection_translation("fingering_finger", "y")):
                with self.conditional_color(is_special_color, 0,0,1):
                    self.draw_fingering(x, note.degree, fingering_finger, False)
        
        fingering_string = note.extras.get("fingering_string", None)
        if fingering_string is not None:
            is_special_color = config.show_debug("show_selected_object") and "fingering_string" in selection
            with self.conditional_translation("fingering_string" in selection, note.selection_translation("fingering_string", "x"), note.selection_translation("fingering_string", "y")):
                with self.conditional_color(is_special_color, 0,0,1):
                    self.draw_fingering(x, note.degree, fingering_string, True)