from io import BytesIO

import numpy as np
from cairo import FORMAT_ARGB32, Context, ImageSurface

from . import StaffDrawer, get_image, prepare_scoreline_new
from .config import Config

config = Config()


class Score:
    size = (400, 200) #!DEPRECATED
    
    def __init__(self) -> None:
        self.current_id = 0
        self.scorelines: list[StaffDrawer] = []
        self.grouped_line_pairs: list[tuple[int,int]] = []
        # self._line_group_types = {}
    
    def configure(self, params):
        for key, val in params:
            setattr(self, key, val)
    
    #i) REENABLE if we notice that we can see multiple lines in high resolution images
    # def get_line_group_type(self, line_id: int) -> str:
    #     return self._line_group_types.get(line_id, None)
    
    # def set_line_group_type(self, line_id: int, group_type: str) -> None:
    #     if group_type == "start" and self.get_line_group_type(line_id) == "end":
    #         self._line_group_types[line_id] = "both"
    #     else:
    #         self._line_group_types[line_id] = group_type
    
    def add_scoreline(self, grouped_with: StaffDrawer|None = None) -> StaffDrawer:
        scoreline = StaffDrawer()
        scoreline.init()
        scoreline.SCORE_ID = self.current_id
        self.scorelines.append(scoreline)
        if grouped_with:
            grouped_with.in_group_after = True
            scoreline.in_group_after = False
            self.grouped_line_pairs.append((grouped_with.SCORE_ID, scoreline.SCORE_ID))
            # self.set_line_group_type(grouped_with.SCORE_ID, "start")
            # self.set_line_group_type(scoreline.SCORE_ID, "end")
        
        self.current_id += 1
        return scoreline
    
    def intersect_grouped_lines(self):
        "Computes the intersection of grouped lines"
        pass
    
    def prepare_layout_positions(self):
        "Computes the layout of the score"
        N = len(self.scorelines)
        x = 0
        y = 0
        layout_positions = []
        for i in range(N):
            height = self.sizes[i, 1]
            margin = config("STAVES_GROUP_SPACE") if self.scorelines[i].in_group_after else config("STAVES_SPACE")
            layout_positions.append((x, y))
            y += height + margin
        return layout_positions
    
    def finalize(self):
        staves_margin = config("STAVES_SPACE")
        sizes, surfaces = self.finish_frames()
        N = len(self.scorelines)
        
        # get max width and total height
        max_width = int(sizes[:, 0].max())
        total_height = int(sizes[:, 1].sum() + (N-1) * staves_margin)
        
        final_surface = ImageSurface(FORMAT_ARGB32, max_width, total_height)
        f_ctx = Context(final_surface)

        f_ctx.set_source_rgba(1, 1, 1, 1)
        f_ctx.paint()

        layout_positions = self.prepare_layout_positions()
        print(layout_positions)
        for i in range(N):
            x, y = layout_positions[i]
            f_ctx.set_source_surface(surfaces[i], x, y) #i) this surface was filled in finish_frames()
            f_ctx.paint()
        
        if self.grouped_line_pairs:
            f_ctx.set_line_width(config.STAFF_LW)
            f_ctx.set_source_rgba(0, 0, 0, 1)
            for first, second in self.grouped_line_pairs:
                first_line = self.scorelines[first]
                second_line = self.scorelines[second]
                x = first_line.layout.x
                f_ctx.move_to(x, first_line.top_staff_y + layout_positions[first][1])
                f_ctx.line_to(x, second_line.bottom_staff_y + layout_positions[second][1])
                print(first_line.top_staff_y, first_line.bottom_staff_y, second_line.top_staff_y, second_line.bottom_staff_y)
                print(f"Drawing line from {x}, {first_line.top_staff_y} to {x}, {second_line.bottom_staff_y}")
                f_ctx.stroke()
        
        output = BytesIO()
        final_surface.write_to_png(output)
        return output.getvalue()
    
    def finish_frames(self) -> tuple[list, list]:
        sizes = []
        surfaces = []
        for scoreline in self.scorelines:
            size = scoreline.layout.autolayout_from_registered()
            surface = ImageSurface(
                FORMAT_ARGB32, int(size[0]), int(size[1])
            )
            ctx = Context(surface)
            ctx.set_source_rgba(1, 1, 1, 0)
            ctx.paint()

            ctx.set_source_rgb(0, 0, 0)
            scoreline.ctx = ctx
            # scoreline.noteDrawer.ctx = ctx
            # scoreline.beamedGroupHandler.ctx = ctx
            # scoreline.symbolDrawer.ctx = ctx
            
            scoreline.place_registered()
            scoreline.draw_lines()
            scoreline.draw_clef()
            
            sizes.append(size)
            surfaces.append(surface)
        sizes = np.array(sizes) # shape: N, 2 (width, height)
        self.sizes = sizes
        self.surfaces = surfaces
        return sizes, surfaces
    
    def get_image(self):
        #!DEPRECATED
        N = len(self.scorelines)
        total_height = N*self.size[1] + (N-1)*config("STAVES_SPACE")
        final_surface = ImageSurface(FORMAT_ARGB32, self.size[0], total_height)
        f_ctx = Context(final_surface)

        f_ctx.set_source_rgba(1, 1, 1, 1)
        f_ctx.paint()

        x = 0
        y = 0
        for line in self.scorelines:
            f_ctx.set_source_surface(line.frame, x, y)
            f_ctx.paint()
            y += self.size[1] + config("STAVES_SPACE")
        
        output = BytesIO()
        final_surface.write_to_png(output)
        return output.getvalue()
    
def score_from_json(body: dict):
    the_score = Score()

    for line in body.get('lines'):
        scoreline = the_score.add_scoreline()
        for items in line:
            key = items.get('type')
            args = items.get('options')
            scoreline.layout.register(key, **args)

    return the_score.finalize()