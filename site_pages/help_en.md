## Music Staff Configuration

- Use `BEGIN line` to start a new staff or add a line.
- Use `BEGIN grouped` to add a line connected to the previous one.
- Use `SET clef_sharp N` to set the number of sharps (N) at the clef.
- Use `SET clef_flat N` to set the number of flats (N) at the clef.
- Use `SIGNATURE 3 4`, `SIGNATURE 2 4`, etc., or `SIGNATURE C` to specify the time signature.

![](/static/staff.png)

## Adding Notes

Adding a note requires at a minimum its **degree**. Other parameters follow a specific order.
Here is a complete example of a note with all possible options: `bmi+.! "Lorem" ((2)) (4)`

<div class="text-3xl">
<div class="fragment text-red-600">
    <span class="bg-red-100">b</span><span>accidental</span>
</div>
<div class="fragment text-blue-600">
    <span class="border bg-blue-100 border-blue-600">mi</span><span><b>degree</b></span>
</div>
<div class="fragment text-blue-600">
    <span class="bg-blue-100">+</span><span>+1 octave</span>
</div>
<div class="fragment">
    <span class="bg-gray-100">.</span><span>dotted</span>
</div>
<div class="fragment">
    <span class="bg-gray-100">!</span><span>downward</span>
</div>
<div class="fragment text-orange-600">
    <span class="bg-orange-100">"Lorem"</span><span>lyrics</span>
</div>
<div class="fragment text-blue-400">
    <span class="bg-blue-50">((2))</span><span>string</span>
</div>
<div class="fragment text-green-600">
    <span class="bg-green-100">(4)</span><span>fingering</span>
</div>
</div>

![](/static/note_example.png)

#### Note Degree

The degree must be noted either with the number of the note (1 = C base), or with its name and as many `+` or `-` as octaves of offset.

- `do` corresponds to the base C, or `1`.
- `re` corresponds to D, or `2`.
- `do+` corresponds to the octave above C, or `8`.
- `mi--` corresponds to the E, two octaves below the reference C, or the low E of the guitar.

To change the duration of the note (whole, half, quarter, etc.), use `SET duration N`, where N=0 for a whole note, 1 for a half note, 2 for a quarter note, etc.

#### Accidentals

Place these symbols before the note:

- `#` for a sharp.
- `b` for a flat.
- `n` for a natural note (becarre).

![](/static/alterations.png)

#### Additional Options

These options are placed after the note:

- `.` for a dotted note, which lasts 50% longer.
- `!` for the note stem to be oriented downwards.

![](/static/modifiers.png)

#### Lyrics

After the options, you can associate lyrics with the note by placing them between quotes

- `do "Lo" re "-rem"` will display "Lo-rem" under the corresponding notes.

![](/static/lyrics.png)

#### Guitar Fingering

To indicate the string number (which appears in a circle) and/or the finger to use:

- `la ((3))` to play A on the 3nd string.
- `la (2)` to play A with the second finger.
- `la ((3)) (2)` to play A on the 3nd string with the second finger.

![](/static/fingering.png)

#### Rests

The rest is represented by `_`, it will correspond to the duration defined by the last `SET DURATION`.

![](/static/rests.png)

## Chords and Triplets

Chords are indicated by notes in parentheses, and tied eighth notes by brackets:

- `(do mi sol)` for a C major chord.
- `[re mi] [mi fa] [re fa]` for three groups of two tied eighth notes.

![](/static/chords.png)

To have chords and groups oriented downwards, add a `!` after the parentheses or brackets.

## Measure Bars and Repeats

There are different styles of end-of-measure bars, they are noted with `|` and `:`. If the bar is doubled, the thicker side is noted with a bracket:

`|` `||` `|:` `:|` `[|` `|]` `[|:` `:|]`

![](/static/bars.png)

## Advanced Spacing Commands

- `MOVE X forward` or `MOVE X back` to add or remove space. `X` represents the size of the space; `1` is the space after a quarter note; `0.33` is the space of a sharp or flat. ![](/static/move.png)
- `SELECT 'symbol'` to select a previously added symbol, like `SELECT '#'` for the last sharp or `SELECT '(2)'` for fingering number 2.
- `TRANSLATE x y` to move the selected element horizontally (x) and vertically (y), for example, `TRANSLATE 10 -5` will move it 10 units to the right and 5 units down.

> Example of the usefulness of the `SELECT`/`TRANSLATE` commands: by default, the string indication is in the place of B. So it is moved down with `TRANSLATE 0 1.75`
> 
> ![](/static/translate.png)

The `SELECT` command allows you to select:

- The accidentals `#`, `b`, `n`
- The dots of dotted notes `.`
- The fingerings (example `(2)`)
- The string numbers (example `((6))`)