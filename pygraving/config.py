from math import pi


class Config:
    #* MAIN ABSOLUTE VALUES IN PIXELS
    STAFF_LINE_HEIGTH = 20
    STAFF_LW = 2
    STEM_LW = 3
    #i) The rest are multipliers
    
    # STAFF
    STAVES_SPACE = 1.5
    STAFF_ORIGIN_POSITION_BASE = 1.3
    CLEF_ALTERATIONS_SPACE = 0.33
    
    # Notes
    NOTE_SPACE = 3.5
    NOTE_ELLIPSE_BASE_WIDTH = 20.0/15.0
    NOTE_ELLIPSE_BASE_HEIGHT = 1.0
    NOTE_STEM_Y_OFFSET = 0.15
    NOTE_HOLE_SCALE_X = 0.9
    NOTE_HOLE_SCALE_Y = 0.6
    NOTE_ANGLE = -pi/8
    NOTE_HELPER_LINE_PADDING_COEFF = 0.166
    
    # Dots
    NOTE_DOT_RADIUS = 0.166
    DOT_X_OFFSET = 0.75
    DOT_Y_OFFSET = 0.5
    
    # Stem
    STEM_LENGTH = 3.0
    
    # Beamed groups
    STEM_MIN_LENGTH = 2.0
    BEAM_THICKNESS = 0.5
    BEAM_LINE_SPACE = 1.25
    
    # Voice track
    VOICE_FONT_FACE = "Times New Roman"
    LYRICS_SPACE = 1.5
    VOICE_FONT_SIZE = 24