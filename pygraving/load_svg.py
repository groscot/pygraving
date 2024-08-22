from io import BytesIO

import cairo
import pyparsing


def tokenize_path(p):
    dot = pyparsing.Literal(".")
    comma = pyparsing.Literal(",").suppress()
    floater = pyparsing.Combine(pyparsing.Optional("-") +
        pyparsing.Word(pyparsing.nums) +
        pyparsing.Optional(dot) +
        pyparsing.Optional(pyparsing.Word(pyparsing.nums)))
    # Unremark to have numbers be floats rather than strings.
    floater.setParseAction(lambda toks:float(toks[0]))
    couple = floater + pyparsing.Optional(comma) + floater

    M_command = "M" + pyparsing.Group(couple)
    C_command = "C" + pyparsing.Group(couple + couple + couple)
    L_command = "L" + pyparsing.Group(couple)
    Z_command = "Z"
    
    svgcommand = M_command | C_command | L_command | Z_command
    phrase = pyparsing.OneOrMore(pyparsing.Group(svgcommand))
    tokens = phrase.parseString(p.upper())
    return tokens

def apply_tokens(tokens, ctx):
    for value in tokens:
        command = value[0]
        if command == "Z":
            ctx.close_path()
            continue
        c = value[1].asList()
        if command == "M":
            ctx.move_to(c[0],c[1])
        if command == "C":
            ctx.curve_to(c[0],c[1],c[2],c[3],c[4],c[5])
        if command == "L":
            ctx.line_to(c[0],c[1])

def create_surface_from_svg_path(filepath: str, size: tuple = (800, 800), matrix=None) -> cairo.SVGSurface:
    "! DEPRECATED"
    output = BytesIO()
    surface = cairo.SVGSurface(output, *size)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0, 0, 0)
    if matrix is not None:
        ctx.set_matrix(cairo.Matrix(*matrix))

    p = open(filepath).read()
    tokens = tokenize_path(p)
    
    apply_tokens(tokens, ctx)
    ctx.fill()
    return surface

def svg_path_to_ctx_fill(filepath: str, matrix=None) -> callable:
    p = open(filepath).read()
    tokens = tokenize_path(p)
    
    def draw(ctx):
        if matrix is not None:
            ctx.set_matrix(cairo.Matrix(*matrix))
        apply_tokens(tokens, ctx)
        ctx.fill()
    
    return draw