## Configuration de la portée musicale

- Utilisez `BEGIN line` pour commencer une nouvelle portée ou ajouter une ligne.
- Utilisez `BEGIN grouped` pour ajouter une ligne connectée à la précédente.
- Utilisez `SET clef_sharp N` pour définir le nombre de dièses (N) à la clé.
- Utilisez `SET clef_flat N` pour définir le nombre de bémols (N) à la clé.
- Utilisez `SIGNATURE 3 4`, `SIGNATURE 2 4`, etc., ou `SIGNATURE C` pour spécifier la mesure.

![](/static/staff.png)

## Ajout de notes

L'ajout d'une note nécessite au minimum son **degré**. Les autres paramètres suivent un ordre spécifique.
Voici un exemple complet d'une note avec toutes les options possibles : `bmi+.! "Lorem" ((2)) (4)`

<div class="text-3xl">
<div class="fragment text-red-600">
    <span class="bg-red-100">b</span><span>altération</span>
</div>
<div class="fragment text-blue-600">
    <span class="border bg-blue-100 border-blue-600">mi</span><span><b>degré</b></span>
</div>
<div class="fragment text-blue-600">
    <span class="bg-blue-100">+</span><span>+1 octave</span>
</div>
<div class="fragment">
    <span class="bg-gray-100">.</span><span>pointée</span>
</div>
<div class="fragment">
    <span class="bg-gray-100">!</span><span>vers le bas</span>
</div>
<div class="fragment text-orange-600">
    <span class="bg-orange-100">"Lorem"</span><span>paroles</span>
</div>
<div class="fragment text-blue-400">
    <span class="bg-blue-50">((2))</span><span>corde</span>
</div>
<div class="fragment text-green-600">
    <span class="bg-green-100">(4)</span><span>doigté</span>
</div>
</div>

![](/static/note_example.png)

#### Degré de la note

Le degré doit être noté soit avec le numéro de la note (1 = do de base), soit avec son nom et autant de `+` ou de `-` que d'octaves de décalage.

- `do` correspond au do de base, soit `1`.
- `re` correspond au ré, soit `2`.
- `do+` correspond à l'octave supérieure de do, soit `8`.
- `mi--` correspond au mi, deux octaves en-dessous du do de référence, soit le mi grave de la guitare.

Pour changer la durée de la note (ronde, blanche, noire, etc.), utilisez `SET duration N`, où N=0 pour une ronde, 1 pour une blanche, 2 pour une noire, etc.

#### Altérations

Placez ces symboles avant la note :

- `#` pour un dièse.
- `b` pour un bémol.
- `n` pour une note naturelle (bécarre).

![](/static/alterations.png)

#### Options supplémentaires

Ces options se placent après la note :

- `.` pour une note pointée, qui dure 50% plus longtemps.
- `!` pour que la queue de la note soit orientée vers le bas.

![](/static/modifiers.png)

#### Paroles

Après les options, vous pouvez associer des paroles à la note en les plaçant entre guillemets

- `do "Lo" re "-rem"` affichera "Lo-rem" sous les notes correspondantes.

![](/static/lyrics.png)

#### Doigté pour guitare

Pour indiquer le numéro de la corde (qui apparaît dans un cercle) et/ou le doigt à utiliser :

- `la ((3))` pour jouer la sur la 3ème corde.
- `la (2)` pour jouer la avec le deuxième doigt.
- `la ((3)) (2)` pour jouer la sur la 3ème corde avec le deuxième doigt.

![](/static/fingering.png)

#### Silence

Le silence est représenté par `_`, il correspondra à la durée définie par le dernier `SET DURATION`.

![](/static/rests.png)

## Accords et triolets

Les accords sont indiqués par des notes entre parenthèses, et les croches liées par des crochets :

- `(do mi sol)` pour un accord de Do majeur.
- `[re mi] [mi fa] [re fa]` pour trois groupes de deux croches liées.

![](/static/chords.png)

Pour que les accords et les groupes soient orientés vers le bas, ajoutez un `!` après les parenthèses ou les crochets.

## Barres de mesure et répétitions

Il existe différents styles de barres de fin de mesure, elles se notent avec des `|` et des `:`. Si la barre est doublée, le côté plus épais se note avec un crochet :

`|` `||` `|:` `:|` `[|` `|]` `[|:` `:|]`

![](/static/bars.png)

## Commandes d'espacement avancé

- `MOVE X forward` ou `MOVE X back` pour ajouter ou retirer de l'espace. `X` représente la taille de l'espace ; `1` est l'espace après une noire ; `0.33` est l'espace d'un dièse ou d'un bémol. ![](/static/move.png)
- `SELECT 'symbol'` pour sélectionner un symbole ajouté précédemment, comme `SELECT '#'` pour le dernier dièse ou `SELECT '(2)'` pour le doigté numéro 2.
- `TRANSLATE x y` pour déplacer l'élément sélectionné horizontalement (x) et verticalement (y), par exemple, `TRANSLATE 10 -5` le déplacera de 10 unités à droite et de 5 unités vers le bas.

> Exemple de l'utilité des commandes `SELECT`/`TRANSLATE` : par défaut, l'indication de corde est à la place du si. On la décale donc vers le bas avec `TRANSLATE 0 1.75`
> 
> ![](/static/translate.png)

La commande `SELECT` permet de sélectionner :

- Les altérations `#`, `b`, `n`
- Les points des notes pointées `.`
- Les doigtés (exemple `(2)`)
- Les numéros de corde (exemple `((6))`)