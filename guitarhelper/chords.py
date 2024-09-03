from app import make_preview

# Mapping of degrees to semitones
degree_to_semitone = {
    1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11
}

base_string_degrees = [-4, -1, 2, 5, 7, 10]

# manually set the base string semitones
base_string_semitones = [-8, -3, 2, 7, 11, 16] 

def string_positions_to_degrees(positions: list[int]):
    assert len(positions) == 6
    notes = []
    for i in range(6):
        if positions[i] is not None:
            base_semitone = base_string_semitones[i]
            total_semitones = base_semitone + positions[i]
            
            # Calculate octave and degree
            octave = total_semitones // 12
            semitone_in_octave = total_semitones % 12
            
            # Find the corresponding degree using cumulative sum strategy
            degree = 1
            cumulative_semitones = 0
            while cumulative_semitones < semitone_in_octave:
                cumulative_semitones += degree_to_semitone[degree + 1] - degree_to_semitone[degree]
                degree += 1
            
            if cumulative_semitones > semitone_in_octave:
                degree -= 1
                modifier = "#"
            elif cumulative_semitones < semitone_in_octave:
                modifier = "b"
            else:
                modifier = ""
            # degree = next((d for d, s in degree_to_semitone.items() if s == semitone_in_octave), 0)
            # if degree == 0:
            #     degree = 7
            
            # Handle sharps and flats
            modifier = ""
            if semitone_in_octave in [1, 3, 6, 8, 10]:
                if semitone_in_octave in [1, 6]:
                    modifier = "#"
                else:
                    modifier = "b"
            
            degree += 7*octave
            
            notes.append(modifier + str(degree))
    return notes

def draw_chord(positions: list[int], separated: bool = False):
    degrees = string_positions_to_degrees(positions)
    body = "BEGIN line\n"
    if not separated:
        body += "("
    body += " ".join([f"{degree}" for degree in degrees])
    if not separated:
        body += ")"
    return make_preview(body)