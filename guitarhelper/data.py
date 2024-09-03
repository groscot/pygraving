scales = {
    "major"            : [0,    2,    4, 5,    7,    9,     11],
    "minor"            : [0,    2, 3,    5,    7, 8,    10    ],
    "dorian"           : [0,    2, 3,    5,    7,    9, 10    ],
    "phrygian"         : [0, 1,    3,    5,    7, 8,    10    ],
    "minor_pentatonic" : [0,       3,    5,    7,       10    ],
    "major_pentatonic" : [0,    2,    4,       7,    9        ],
    "harmonic_minor"   : [0,    2, 3,    5,    7, 8,    10    ],
    "aeolian"          : [0,    2, 3,    5,    7, 8,    10    ],
    "minor_blues"      : [0,       3,    5, 6, 7,       10    ],
    "locrian"          : [0, 1,    3,    5, 6,    8,    10    ],
    "lydian"           : [0,    2,    4,    6, 7,    9,     11]
}

chords = {
  "major": {
    "5": [False, 0, 2, 2, 2, False],
    "6": [0, 2, 2, 1, 0, 0]
  },
  "minor": {
    "5" : [False, 0, 2, 2, 1, False],
    "6" : [0, 2, 2, 0, 0, 0]
  },
  "aug": {
    "5": [],
    "6": []
  },
  "dim": {
    "5": [],
    "6": []
  },
  "minor6th": {
    "5": [],
    "6": []
  },
  "major7th": {
    "5": [False, 0, 2, 1, 2, False],
    "6": [0, False, 1, 1, 0, False]
  },
  "7th": {
    "5": [False, 0, 2, 0, 2, False],
    "6": [0, False, 0, 0, 0, False]
  },
  "minor7th": {
    "5" : [False, 0, 2, 0, 1, False],
    "6" : [0, False, 0, 0, 0, False]
  },
  "minor7th-flatted5th": {
    "5": [],
    "6": []
  },
  "omit3": {
    "5": [],
    "6": []
  },
  "sus4": {
    "5": [False,0,0,0,0,0],
    "6": [0,2,0,2,0,False],
    "5'": [False,0,2,0,3,0],
    "6'": [0,False,0,-1,-2]
  },
  "add9": {
    "5": [],
    "6": []
  }
}

guitar_chords = {
    # Open chords
    "C": {"name": "C Major", "positions": [None, 3, 2, 0, 1, 0]},
    "D": {"name": "D Major", "positions": [None, None, 0, 2, 3, 2]},
    "E": {"name": "E Major", "positions": [0, 2, 2, 1, 0, 0]},
    "F": {"name": "F Major", "positions": [1, 3, 3, 2, 1, 1]},
    "G": {"name": "G Major", "positions": [3, 2, 0, 0, 0, 3]},
    "A": {"name": "A Major", "positions": [None, 0, 2, 2, 2, 0]},
    "B": {"name": "B Major", "positions": [None, 2, 4, 4, 4, 2]},

    # Minor chords
    "Am": {"name": "A Minor", "positions": [None, 0, 2, 2, 1, 0]},
    "Bm": {"name": "B Minor", "positions": [None, 2, 4, 4, 3, 2]},
    "Cm": {"name": "C Minor", "positions": [None, 3, 5, 5, 4, 3]},
    "Dm": {"name": "D Minor", "positions": [None, None, 0, 2, 3, 1]},
    "Em": {"name": "E Minor", "positions": [0, 2, 2, 0, 0, 0]},
    "Fm": {"name": "F Minor", "positions": [1, 3, 3, 1, 1, 1]},
    "Gm": {"name": "G Minor", "positions": [3, 5, 5, 3, 3, 3]},

    # Seventh chords
    "C7": {"name": "C Dominant 7th", "positions": [None, 3, 2, 3, 1, 0]},
    "D7": {"name": "D Dominant 7th", "positions": [None, None, 0, 2, 1, 2]},
    "E7": {"name": "E Dominant 7th", "positions": [0, 2, 0, 1, 0, 0]},
    "G7": {"name": "G Dominant 7th", "positions": [3, 2, 0, 0, 0, 1]},
    "A7": {"name": "A Dominant 7th", "positions": [None, 0, 2, 0, 2, 0]},

    # Major seventh chords
    "Cmaj7": {"name": "C Major 7th", "positions": [None, 3, 2, 0, 0, 0]},
    "Dmaj7": {"name": "D Major 7th", "positions": [None, None, 0, 2, 2, 2]},
    "Fmaj7": {"name": "F Major 7th", "positions": [1, 3, 2, 2, 1, 1]},
    "Gmaj7": {"name": "G Major 7th", "positions": [3, 2, 0, 0, 0, 2]},

    # Minor seventh chords
    "Am7": {"name": "A Minor 7th", "positions": [None, 0, 2, 0, 1, 0]},
    "Dm7": {"name": "D Minor 7th", "positions": [None, None, 0, 2, 1, 1]},
    "Em7": {"name": "E Minor 7th", "positions": [0, 2, 0, 0, 0, 0]},

    # Suspended chords
    "Asus4": {"name": "A Suspended 4th", "positions": [None, 0, 2, 2, 3, 0]},
    "Dsus4": {"name": "D Suspended 4th", "positions": [None, None, 0, 2, 3, 3]},
    "Esus4": {"name": "E Suspended 4th", "positions": [0, 2, 2, 2, 0, 0]},

    # Exotic and diverse chords
    "Cadd9": {"name": "C Add 9", "positions": [None, 3, 2, 0, 3, 0]},
    "Dsus2": {"name": "D Suspended 2nd", "positions": [None, None, 0, 2, 3, 0]},
    "E7#9": {"name": "E Dominant 7th Sharp 9", "positions": [0, 2, 0, 1, 3, 3]},
    "Fmaj9": {"name": "F Major 9th", "positions": [1, 0, 3, 0, 1, 3]},
    "G6": {"name": "G 6th", "positions": [3, 2, 0, 0, 0, 0]},
    "Am11": {"name": "A Minor 11th", "positions": [None, 0, 0, 0, 1, 0]},
    "Bm7b5": {"name": "B Half-Diminished", "positions": [None, 2, 3, 2, 3, None]},

    # Barre chords
    "F_barre": {"name": "F Major (Barre)", "positions": [1, 3, 3, 2, 1, 1]},
    "Bb_barre": {"name": "B-flat Major (Barre)", "positions": [6, 8, 8, 7, 6, 6]},
    "C#m_barre": {"name": "C-sharp Minor (Barre)", "positions": [4, 6, 6, 4, 4, 4]},
    "G#7_barre": {"name": "G-sharp Dominant 7th (Barre)", "positions": [4, 6, 4, 5, 4, 4]},

    # Extended chords
    "Cmaj13": {"name": "C Major 13th", "positions": [None, 3, 2, 2, 0, 1]},
    "D9": {"name": "D Dominant 9th", "positions": [None, 5, 4, 5, 5, None]},
    "E13": {"name": "E Dominant 13th", "positions": [0, 2, 2, 1, 2, 2]},

    # Altered chords
    "G7b9": {"name": "G Dominant 7th Flat 9", "positions": [3, 2, 3, 1, 4, 3]},
    "A7#5": {"name": "A Dominant 7th Sharp 5", "positions": [None, 0, 3, 0, 2, 1]},

    # Diminished and augmented chords
    "Cdim": {"name": "C Diminished", "positions": [None, 3, 4, 2, 4, 2]},
    "Eaug": {"name": "E Augmented", "positions": [0, 3, 2, 1, 1, 0]},

    # Slash chords
    "D/F#": {"name": "D over F-sharp", "positions": [2, None, 0, 2, 3, 2]},
    "Am/C": {"name": "A Minor over C", "positions": [None, 3, 2, 2, 1, 0]},
}