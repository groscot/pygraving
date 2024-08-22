import numpy as np

from .config import Config
from .mixins import HasCairoContext

config = Config()


class BeamedGroup(HasCairoContext):    
    def register_notes(self, notes: list[tuple], durations: list[int] | int, up: bool = True):
        if isinstance(durations, int):
            self._duration = durations
            durations = [durations]*len(notes)
        else:
            self._duration = 1
        
        self.direction = 1 if up else -1
        self.notes = notes
        self.durations = durations
        self.compute_stems_endpoints()
    
    def compute_one_stem_endpoints(self, x0, y0):
        #TODO remove these constants
        lw = config.STEM_LW        
        
        x = config("NOTE_ELLIPSE_BASE_WIDTH") /2 - config.half(lw)
        y_from = -self.direction * config("NOTE_STEM_Y_OFFSET")
        y_to   = -self.direction * config("STEM_LENGTH")
        
        return (x0 + x*self.direction, y0 + y_from, y0 + y_to)
        
    def compute_stems_endpoints(self):
        baseline = []
        for x0, y0 in self.notes:
            baseline.append(self.compute_one_stem_endpoints(x0, y0))
        self.x_start = baseline[0][0]
        self.x_end = baseline[-1][0]
        self.baseline = baseline
        
        # compute heights with extreme points
        y_start = baseline[0][-1]
        y_end = baseline[-1][-1]
        tentative = np.linspace(y_start, y_end, len(self.notes), endpoint=True)
        tentative_lengths = np.abs(np.array([b[1] for b in baseline]) - tentative)
        
        engraved_min_length = config("STEM_MIN_LENGTH")
        if np.min(tentative_lengths) >= engraved_min_length:
            self.y_start = y_start
            self.y_end = y_end
            return
        else:
            blocking_value = np.min(tentative_lengths)
            delta = np.abs(blocking_value - engraved_min_length)
            self.y_start = y_start - self.direction*delta
            self.y_end = y_end - self.direction*delta
            
    def draw_stems(self):
        N = len(self.notes)
        ys = np.linspace(self.y_start, self.y_end, N, endpoint=True)
        for i in range(N):
            x = self.baseline[i][0]
            self.ctx.move_to(x, self.baseline[i][1])
            self.ctx.line_to(x, ys[i])
            self.stroke(config.STEM_LW)
    
    def draw_beam_line(self, thickness, delta_y=0):
        self.ctx.move_to(self.x_start, delta_y + self.y_start)
        self.ctx.line_to(self.x_end, delta_y + self.y_end)
        self.ctx.line_to(self.x_end, delta_y + self.y_end + thickness)
        self.ctx.line_to(self.x_start, delta_y + self.y_start + thickness)
        self.ctx.close_path()
        self.ctx.fill()
        
    def draw_beam(self):
        thickness = self.direction * config("BEAM_THICKNESS")
        n = self._duration
        delta_y = 0
        for _ in range(n):
            self.draw_beam_line(thickness, delta_y)
            delta_y += thickness * config.BEAM_LINE_SPACE
