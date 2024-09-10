import cairo

from .staff_drawer import StaffDrawer

# from ._scoreline import ScoreLine

# helper functions

def prepare_svg_scoreline(size, scoreline_params={}, note_params={}, super_resolution: int = 1):
    from io import BytesIO
    outpt = BytesIO()
    frame_surface = cairo.SVGSurface(outpt, *size)
    ctx = cairo.Context(frame_surface)

    ctx.set_source_rgba(1, 1, 1, 0)
    ctx.paint()

    scoreline = ScoreLine(ctx)
    scoreline.init()
    for key, value in scoreline_params.items():
        if isinstance(value, int) or isinstance(value, float):
            value *= super_resolution
        setattr(scoreline, key, value)
    for key, value in note_params.items():
        if isinstance(value, int) or isinstance(value, float):
            value *= super_resolution
        setattr(scoreline.noteDrawer, key, value)
    scoreline.noteDrawer.SCORE_LINE_HEIGTH = scoreline.lineheight
    
    return scoreline, frame_surface, outpt

def prepare_scoreline(size, scoreline_params={}, note_params={}, super_resolution: int = 1):
    frame_surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, size[0]*super_resolution, size[1]*super_resolution
    )
    ctx = cairo.Context(frame_surface)

    ctx.set_source_rgba(1, 1, 1, 0)
    ctx.paint()

    scoreline = ScoreLine(ctx)
    scoreline.init()
    for key, value in scoreline_params.items():
        if isinstance(value, int) or isinstance(value, float):
            value *= super_resolution
        setattr(scoreline, key, value)
    for key, value in note_params.items():
        if isinstance(value, int) or isinstance(value, float):
            value *= super_resolution
        setattr(scoreline.noteDrawer, key, value)
    scoreline.noteDrawer.SCORE_LINE_HEIGTH = scoreline.lineheight
    scoreline.beamedGroupHandler.SCORE_LINE_HEIGTH = scoreline.lineheight
    
    return scoreline, frame_surface

def prepare_scoreline_new(size, scoreline_params={}, note_params={}, super_resolution: int = 1):
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, size[0]*super_resolution, size[1]*super_resolution
    )
    ctx = cairo.Context(surface)

    ctx.set_source_rgba(1, 1, 1, 0)
    ctx.paint()

    scoreline = ScoreLine(ctx, surface)
    scoreline.init()
    for key, value in scoreline_params.items():
        if isinstance(value, int) or isinstance(value, float):
            value *= super_resolution
        setattr(scoreline, key, value)
    for key, value in note_params.items():
        if isinstance(value, int) or isinstance(value, float):
            value *= super_resolution
        setattr(scoreline.noteDrawer, key, value)
    scoreline.noteDrawer.SCORE_LINE_HEIGTH = scoreline.lineheight
    scoreline.beamedGroupHandler.SCORE_LINE_HEIGTH = scoreline.lineheight
    
    return scoreline

def get_image(frame_surface, size, super_resolution: int = 1):
    from io import BytesIO
    final_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size[0]*super_resolution, size[1]*super_resolution)
    f_ctx = cairo.Context(final_surface)

    f_ctx.set_source_rgba(1, 1, 1, 1)
    f_ctx.paint()

    f_ctx.set_source_surface(frame_surface)
    f_ctx.paint()

    output = BytesIO()
    final_surface.write_to_png(output)
    return output.getvalue()