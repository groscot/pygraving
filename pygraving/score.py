from io import BytesIO

import numpy as np
from cairo import FORMAT_ARGB32, Context, ImageSurface

from . import StaffDrawer, get_image, prepare_scoreline_new
from .config import Config

config = Config()


class Score:
    size = (400, 200) #!DEPRECATED
    
    def __init__(self) -> None:
        self.scorelines: list[StaffDrawer] = []
    
    def configure(self, params):
        for key, val in params:
            setattr(self, key, val)
    
    def add_scoreline(self) -> StaffDrawer:
        scoreline = StaffDrawer()
        scoreline.init()
        self.scorelines.append(scoreline)
        return scoreline
    
    def finalize(self):
        staves_margin = config("STAVES_SPACE")
        sizes, surfaces = self.finish_frames()
        sizes = np.array(sizes) # shape: N, 2 (width, height)
        N = len(self.scorelines)
        
        # get max width and total height
        max_width = int(sizes[:, 0].max())
        total_height = int(sizes[:, 1].sum() + (N-1) * staves_margin)
        
        final_surface = ImageSurface(FORMAT_ARGB32, max_width, total_height)
        f_ctx = Context(final_surface)

        f_ctx.set_source_rgba(1, 1, 1, 1)
        f_ctx.paint()

        x = 0
        y = 0
        for i in range(N):
            # line = self.scorelines[i]
            height = sizes[i, 1]
            f_ctx.set_source_surface(surfaces[i], x, y) #i) this surface was filled in finish_frames()
            f_ctx.paint()
            y += height + staves_margin
        
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