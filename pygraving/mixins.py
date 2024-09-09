from io import BytesIO

from cairo import FORMAT_ARGB32, Context, ImageSurface


class HasCairoContext:
    lw: int = 1
    
    def __init__(self, ctx: Context = None, frame: ImageSurface = None) -> None:
        self.frame = frame
        self.ctx = ctx
        if ctx is not None:
            self.ctx.set_source_rgb(0, 0, 0)
        
    def stroke(self, lw=None):
        lw = lw or self.lw
        self.ctx.set_line_width(lw)
        self.ctx.stroke()
        
    def get_image(self, size, super_resolution: int = 1):
        final_surface = ImageSurface(FORMAT_ARGB32, size[0]*super_resolution, size[1]*super_resolution)
        f_ctx = Context(final_surface)

        f_ctx.set_source_rgba(1, 1, 1, 1)
        f_ctx.paint()

        f_ctx.set_source_surface(self.frame)
        f_ctx.paint()

        output = BytesIO()
        final_surface.write_to_png(output)
        return output.getvalue()
    
    def temporary_color(self, *rgb):
        class TemporaryContext:
            def __init__(self, obj, rgb):
                self.obj = obj
                self.rgb = rgb
            def __enter__(self):
                self.obj.ctx.set_source_rgb(*self.rgb)
            def __exit__(self, *args):
                self.obj.ctx.set_source_rgb(0, 0, 0)
        return TemporaryContext(self, rgb)


class HasParentCairoContext:
    def __init__(self, parent):
        self.parent = parent

    @property
    def ctx(self):
        return self.parent.ctx

    def stroke(self, lw=None):
        self.parent.stroke(lw)
        
    def temporary_color(self, *rgb):
        return self.parent.temporary_color(*rgb)