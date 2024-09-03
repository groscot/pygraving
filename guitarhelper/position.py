import math

import cairo


def draw_chord_diagram(positions, output_file, chord_name=None):
    # Determine the start position and number of frets to show
    start_position = min(pos for pos in positions if pos is not None)
    end_position = max(pos for pos in positions if pos is not None)
    frets_to_show = max(4, end_position - start_position + 1)
    
    # Set up dimensions
    string_spacing = 50
    fret_spacing = 60
    left_margin = 40
    top_margin = 40

    width = 2 * left_margin + 5 * string_spacing
    height = 2 * top_margin + frets_to_show * fret_spacing
    
    # Create cairo surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    # Set background color (white)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    
    # Set color for lines and text (black)
    ctx.set_source_rgb(0, 0, 0)
    
    # Draw strings
    for i in range(6):
        x = left_margin + i * string_spacing
        ctx.move_to(x, top_margin)
        ctx.line_to(x, top_margin + frets_to_show * fret_spacing)
    ctx.set_line_width(1)
    ctx.stroke()
    
    # Draw frets
    for i in range(frets_to_show + 1):
        y = top_margin + i * fret_spacing
        ctx.move_to(left_margin, y)
        ctx.line_to(left_margin + 5 * string_spacing, y)
    ctx.set_line_width(2)
    ctx.stroke()
    
    # Draw start position number (only if greater than 2)
    if start_position > 2:
        ctx.set_font_size(20)
        ctx.move_to(10, top_margin + fret_spacing / 2)
        ctx.show_text(str(start_position))
    
    # Draw finger positions
    for i, pos in enumerate(positions):
        if pos is not None and pos > 0:
            x = left_margin + i * string_spacing
            fret_number = pos - start_position + 0.5
            if start_position == 0:
                fret_number -= 1
            y = top_margin + fret_number * fret_spacing
            ctx.arc(x, y, 15, 0, 2 * math.pi)
            ctx.fill()

    # Draw open and muted strings
    for i, pos in enumerate(positions):
        x = left_margin + i * string_spacing
        if pos == 0:
            ctx.arc(x, top_margin - 15, 10, 0, 2 * math.pi)
            ctx.stroke()
        elif pos is None:
            ctx.set_line_width(2)
            ctx.move_to(x - 10, top_margin - 25)
            ctx.line_to(x + 10, top_margin - 5)
            ctx.move_to(x - 10, top_margin - 5)
            ctx.line_to(x + 10, top_margin - 25)
            ctx.stroke()
    
    # Draw chord name at the bottom
    if chord_name is not None:
        ctx.set_font_size(24)
        fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()
        text_width = ctx.text_extents(chord_name)[2]
        ctx.move_to((width - text_width) / 2, height - fdescent)
        ctx.show_text(chord_name)
    
    # Save the diagram
    surface.write_to_png(output_file)

# Example usage:
# draw_chord_diagram([None, None, 0, 2, 3, 2], "D Major", "D_major_chord.png")
# draw_chord_diagram([3, 2, 0, 0, 0, 3], "G Major", "G_major_chord.png")
# draw_chord_diagram([1, 3, 3, 2, 1, 1], "F Major", "F_major_chord.png")
# draw_chord_diagram([6, 8, 8, 7, 6, 6], "Bb Major (Barre)", "Bb_major_barre_chord.png")