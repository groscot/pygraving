from pygraving.config import config
from pygraving.note import Note

from .auto import AutoLayout
from .commons import GenericLayout, PositionDegreeBounds


class JustifiedLayout(AutoLayout):
    target_length: int = 2000
    justification_factor: float = 1.0
    cutoff_factor: float = 1.5
    
    def position_to_x(self, position: float) -> float:
        return self.x + self.staff_origin_position_base + config("NOTE_SPACE") * position * self.justification_factor
    
    def run(self):
        w, h = super().run()
        unjustified_length = w - 2*self.padding # remove padding from autolayout
        target_length = self.target_length
        
        offset = self.staff_origin_position_base
        target_length -= offset
        unjustified_length -= offset
        
        factor = target_length / unjustified_length
        if factor <= self.cutoff_factor:
            factor = factor
        else:
            factor = 1.0
        
        self.justification_factor = factor
        self.length = factor * unjustified_length + offset
        return self.length + 2*self.padding, h
    