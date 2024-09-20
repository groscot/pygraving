import numpy as np

from .config import config
from .mixins import HasParentCairoContext
from .note import Note


class BeamedGroup(HasParentCairoContext):
    def init(self, position: float, notes: list[dict], base_duration: int = 1, up: bool = True):
        self.position = position
        self.direction = 1 if up else -1
        self.base_duration = base_duration
        self.debug_positions = []
        
        self.prepare_notes(notes)
        self.process_durations()
        self.compute_stems_endpoints()
    
    def prepare_notes(self, notes):
        self.notes = []
        for _note in notes:
            note = Note.from_token(_note)
            note.beamed = True
            if self.direction == -1:
                note.modifiers += "!"
            self.notes.append(note)
        self.N = len(notes)
    
    def process_durations(self):
        durations = [note.duration for note in self.notes]
        # only do something if the durations are not all the same
        if len(set(durations)) > 1:
            self.note_durations = [max(d - 3, 0) for d in durations]
        else:
            self.note_durations = [0] * len(durations)
    
    def determine_blocking_note(self, notes_real_y, ascending: bool = True):
        # we cannot do a simple argmin or argmax because the beam can be ascending or descending
        # and that will change the blocking note if several notes have the same y coordinate
        blocking_value = np.min(notes_real_y) if self.direction == 1 else np.max(notes_real_y)
        candidates = np.where(notes_real_y == blocking_value)[0]
        if self.direction == 1:
            index = 0 if ascending else -1
        else:
            index = -1 if ascending else 0
        blocking_note_index = candidates[index]
        return blocking_note_index
    
        blocking_note_index = np.argmin(notes_real_y) if self.direction == 1 else np.argmax(notes_real_y)
        return blocking_note_index
    
    def compute_stems_endpoints_old_strategy(self):
        baseline = []
        for i, note in enumerate(self.notes):
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
            #! this formula has failing edge cases! example: [do si re re re si+]
            #i) the reason is that as the beam moves up, the height function is not always monotonous
            blocking_value = np.min(tentative_lengths) 
            delta = np.abs(blocking_value - engraved_min_length)
            #!---
            self.y_start = y_start - self.direction*delta
            self.y_end = y_end - self.direction*delta
    
    def compute_stems_endpoints(self):
        baseline = []
        for i, note in enumerate(self.notes):
            x0 = self.parent.layout.position_to_x(self.position + i)
            y0 = self.parent.layout.degree_to_y(note.degree)
            a,b,c,_ = note.compute_one_stem_endpoints(x0=x0, y0=y0)
            baseline.append((a,b,c))
        self.x_start = baseline[0][0]
        self.x_end = baseline[-1][0]
        y_start = baseline[0][-1]
        y_end = baseline[-1][-1]
        self.baseline = baseline
        
        delta_y = y_end - y_start
        
        # 1. clip the slope
        slope = delta_y / (self.x_end - self.x_start)
        max_slope = config("BEAM_MAX_SLOPE")
        slope = np.clip(slope, -max_slope, max_slope)
        delta_y = slope * (self.x_end - self.x_start)
        
        # 2. clip the absolute difference
        max_diff = config("BEAM_MAX_Y_DIFFERENCE")
        delta_y = np.clip(delta_y, -max_diff, max_diff)
        
        y_end = y_start + delta_y
        
        # compute heights with extreme points
        tentative = np.linspace(y_start, y_end, len(self.notes), endpoint=True)
        notes_real_y = np.array([b[1] for b in baseline])
        tentative_lengths = np.abs(notes_real_y - tentative)        
        
        self.y_start = y_start
        self.y_end = y_end

        engraved_min_length = config("STEM_MIN_LENGTH")
        if np.min(tentative_lengths) >= engraved_min_length:
            self.y_start = y_start
            self.y_end = y_end
            return
        else:
            blocking_note_index = self.determine_blocking_note(notes_real_y, y_end < y_start)
            previous_beam_position = tentative[blocking_note_index]
            
            if config.show_debug("show_beam_block_note"):
                self.debug_positions.append((baseline[blocking_note_index][0], previous_beam_position))
                
            fixed_beam_position = notes_real_y[blocking_note_index] - self.direction * engraved_min_length
            delta = previous_beam_position - fixed_beam_position
            
            self.y_start = y_start - delta
            self.y_end = y_end - delta
            
    def draw_stems(self):
        ys = np.linspace(self.y_start, self.y_end, self.N, endpoint=True)
        for i in range(self.N):
            x = self.baseline[i][0]
            self.ctx.move_to(x, self.baseline[i][1])
            self.ctx.line_to(x, ys[i])
            self.stroke(config.STEM_LW)
            
        if config.show_debug("show_beam_block_note"):
            with self.temporary_color(1,0,0):
                for x,y in self.debug_positions:
                    self.ctx.arc(x, y, 5, 0, 2*np.pi)
                    self.ctx.fill()
    
    def draw_beam_line(self, thickness, delta_y=0, x_start=None, x_end=None):
        if x_start is None:
            x_start = self.x_start
        if x_end is None:
            x_end = self.x_end
        
        # Linear interpolation for y_start and y_end
        total_x_range = self.x_end - self.x_start
        total_y_range = self.y_end - self.y_start
        
        if total_x_range != 0:
            y_start = self.y_start + (x_start - self.x_start) * total_y_range / total_x_range
            y_end = self.y_start + (x_end - self.x_start) * total_y_range / total_x_range
        else:
            y_start = self.y_start
            y_end = self.y_end
        
        self.ctx.move_to(x_start, delta_y + y_start)
        self.ctx.line_to(x_end, delta_y + y_end)
        self.ctx.line_to(x_end, delta_y + y_end + thickness)
        self.ctx.line_to(x_start, delta_y + y_start + thickness)
        self.ctx.close_path()
        self.ctx.fill()
    
    def draw_beam(self):
        thickness = self.direction * config("BEAM_THICKNESS")
        max_duration = max(self.note_durations)
        delta_y = 0
        
        for beam_level in range(max_duration + 1):
            i = 0
            while i < self.N:
                if self.note_durations[i] >= beam_level:
                    start = i
                    while i < self.N and self.note_durations[i] >= beam_level:
                        i += 1
                    end = i - 1
                    
                    if start == end:
                        # Isolated note, draw partial beams
                        if start > 0:
                            x_start = (self.baseline[start - 1][0] + self.baseline[start][0]) / 2
                        else:
                            x_start = self.baseline[start][0]
                        
                        if end < self.N - 1:
                            x_end = (self.baseline[end][0] + self.baseline[end + 1][0]) / 2
                        else:
                            x_end = self.baseline[end][0]
                        
                        self.draw_beam_line(thickness, delta_y, x_start, x_end)
                    else:
                        # Contiguous segment, draw full beam
                        x_start = self.baseline[start][0]
                        x_end = self.baseline[end][0]
                        self.draw_beam_line(thickness, delta_y, x_start, x_end)
                else:
                    i += 1
            
            delta_y += thickness * config.BEAM_LINE_SPACE

    def get_notes_for_registration(self) -> list[Note]:
        ys = np.linspace(self.y_start, self.y_end, self.N, endpoint=True)
        notes = []
        for i, note in enumerate(self.notes):
            note.stem_length = np.abs(ys[i] - self.baseline[i][1]) + config("BEAM_THICKNESS")
            notes.append((self.position + i, note))
        return notes