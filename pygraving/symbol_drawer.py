import os
import pathlib
from math import pi

from .config import Config
from .load_svg import svg_path_to_ctx_fill
from .mixins import HasParentCairoContext

config = Config()

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
    [f"silence_{type}" for type in ["whole", "half", "quarter", "eighth", "sixt"]]

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