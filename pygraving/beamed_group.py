import numpy as np

from .config import Config
from .mixins import HasParentCairoContext
from .note import Note

config = Config()


class BeamedGroup(HasParentCairoContext):
    def init(self, position: float, notes: list[Note], durations: list[int] | int, up: bool = True):
        if isinstance(durations, int):
            self._duration = durations
            durations = [durations]*len(notes)
        else:
            self._duration = 1
        
        self.position = position
        self.direction = 1 if up else -1
        self.notes = notes
        self.durations = durations
        self.compute_stems_endpoints()
    
    def compute_stems_endpoints(self):
        baseline = []
        for i, _note in enumerate(self.notes):
            params = Note.parse_note_token(_note)
            note = Note(**params)
            x0 = self.parent.layout.position_to_x(self.position + i)
            y0 = self.parent.layout.degree_to_y(note.degree)
            a,b,c,_ = note.compute_one_stem_endpoints(x0=x0, y0=y0)
            baseline.append((a,b,c))
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
        print(self.y_start, self.y_end)
        for i in range(N):
            x = self.baseline[i][0]
            print(x, self.baseline[i][1], ys[i])
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
