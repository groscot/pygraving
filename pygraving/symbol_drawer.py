import os
import pathlib
from math import atan2, pi

from .config import config
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasParentCairoContext

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

SYMBOLS_DEFAULT_HEIGHT = 25

SYMBOLS_OTHER_HEIGHT = {
    "clef_F": 20,
}

BASE_SYMBOLS = \
    ["sharp", "flat", "natural"] + \
    [f"clef_{clef}" for clef in ["G", "F"]] + \
    [f"signature_digit_{i}" for i in range(10)] + \
    [f"signature_C"] + \
    [f"silence_{type}" for type in ["whole", "half", "quarter", "eighth", "sixt"]] + \
    ["slur_bottom", "slur_top"]

def resolve_align(width: float, align: str) -> float:
    if align == "c":
        return -width/2
    if align == "l":
        return width
    else:
        return -width

class SymbolDrawer(HasParentCairoContext):
    def init(self):
        self.SYMBOLS_OTHER_HEIGHT = SYMBOLS_OTHER_HEIGHT
        self.DRAW_SYMBOL = {}
        for elem in BASE_SYMBOLS:
            self.load_symbol(elem)
            
    def load_symbol(self, name, height=None):
        self.DRAW_SYMBOL[name] = svg_path_to_ctx_fill( current_path / f"shapes/{name}.txt" )
        if height:
            self.SYMBOLS_OTHER_HEIGHT[name] = height
    
    def draw(self, symbol, position: float = None, degree: int = None, x_offset: float = 0):
        scale = config.STAFF_LINE_HEIGHT/self.SYMBOLS_OTHER_HEIGHT.get(symbol, SYMBOLS_DEFAULT_HEIGHT)
        self.ctx.save()
        
        if x_offset or position or degree:
            x = self.parent.layout.position_to_x(position) if position else 0
            y = self.parent.layout.degree_to_y(degree) if degree else 0
            self.ctx.translate(x + x_offset, y)
        
        self.ctx.scale(scale, scale)
        self.DRAW_SYMBOL[symbol](self.ctx)
        self.ctx.restore()
        
    #************************
    
    def draw_dot(self, x: int, y: int):
        radius = config("NOTE_DOT_RADIUS")
        self.ctx.arc(x, y, radius, 0, 2*pi)
        self.ctx.fill()
    
    def draw_alteration(self, which="sharp", align: str = "r", x_offset: float = 0):
        t_x = resolve_align(config("NOTE_ELLIPSE_BASE_WIDTH") + x_offset, align)
        self.draw(which, x_offset=t_x)
    
    def draw_signature_digits(self, digit_1: int, digit_2: int):
        #! giving position=0 doesn't work because the 0 position is changed
        self.draw(f"signature_digit_{digit_1}", degree=8)
        self.draw(f"signature_digit_{digit_2}", degree=4)
        
    def draw_signature_C(self):
        #! giving position=0 doesn't work because the 0 position is changed
        self.draw("signature_C", degree=6)
        
    def draw_silence(self, type: str, position: int, degree: int = 6):
        self.draw(f"silence_{type}", position=position, degree=degree)
        
    def draw_slur(self, start_x, start_degree, end_x, end_degree, direction = 1):
        # This function stretches the slur symbol between two notes
        # as the original symbol is straight
        
        start_y = self.parent.layout.degree_to_y(start_degree)
        end_y = self.parent.layout.degree_to_y(end_degree)
        
        y_space = config("SLUR_TO_NOTE_SPACE") * direction
        
        if config.show_debug("show_slur_endpoints"):
            with self.temporary_color(1, 0, 0):
                self.ctx.arc(start_x, start_y+y_space, 5, 0, 2*pi)
                self.ctx.stroke()
                self.ctx.arc(end_x, end_y+y_space, 5, 0, 2*pi)
                self.ctx.stroke()
        
        #i) the loaded slur symbol draws with a width of 2.15 NOTE_SPACE
        #i) (determined experimentally)
        
        #* Manually determine the affine transformation to the context

        angle = atan2(end_y - start_y, end_x - start_x)
        self.ctx.save()
        self.ctx.translate(start_x, start_y+y_space)
        
        length = ((end_y - start_y)**2 + (end_x - start_x)**2)**0.5
        scale = length
        scale = scale / config.STAFF_LINE_HEIGHT / 2.125 # normalize to page coordinates
        self.ctx.scale(scale, scale)
        self.ctx.rotate(angle)
        
        # just applying the raw scale makes the thickness of the line
        # go crazy for long slurs, so we adjust it
        self.ctx.scale(1, 1/(scale**0.7))
        
        # cannot use slur_top because the sizing is a bit different
        # so instead we use slur_bottom and flip it
        self.ctx.scale(1, direction)
        
        self.draw("slur_bottom") # if direction == 1 else "slur_top")
        self.ctx.restore()