<div class="my-2 p-2 bg-blue-100 text-blue-800">
    <b>Information</b> : la page Exemples met en avant des exemples de commandes à essayer. Vous pourrez les importer dans l'éditeur en un clic pour les tester.
</div>
<div class="my-2 p-2 bg-red-100 text-red-800">
    <b>Attention</b> : une erreur dans le code peut mener à une partition qui s'arrête de façon abrupte.
</div>

## Configuration de la portée

- Utilisez `BEGIN line` pour commencer une nouvelle portée ou ajouter une ligne.
- Utilisez `BEGIN grouped` pour ajouter une ligne connectée à la précédente.
- Utilisez `SET clef_sharp N` pour définir le nombre de dièses (N) à la clé.
- Utilisez `SET clef_flat N` pour définir le nombre de bémols (N) à la clé.
- Utilisez `SIGNATURE 3 4`, `SIGNATURE 2 4`, etc., ou `SIGNATURE C` pour spécifier la mesure.

![](/static/staff.png)

## Durée des notes

Lorsqu'on rajoute une note (section suivante), ce sera par défaut une noire. Pour changer la durée par défaut des notes suivantes, on utiliser la commande `SET duration X`, où `X` est un nombre qui représente le type de note :

- `0` : ronde
- `1` : blanche
- `2` : noire
- `3` : croche
- `4` : double croche

> ```
> BEGIN line  
> do re SET duration 3 mi fa sol SET duration 1 fa
> ```
> 
> ![](/static/durations.png)

## Ajouter une note

L'ajout d'une note nécessite au minimum son **degré**. Les autres paramètres suivent un ordre spécifique.
Voici un exemple complet d'une note avec toutes les options possibles : `bmi+.! "Lorem" ((2)) (4)`

<div class="fragments-parent">
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
<div class="fragment text-purple-600">
    <span class="bg-purple-100">:2</span><span>durée</span>
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

#### Altérations

Placez ces symboles avant la note :

- `#` pour un dièse.
- `b` pour un bémol.
- `n` pour une note naturelle (bécarre).

![](/static/alterations.png)

#### Durée

On peut décider d'ignorer la durée spécifiée par `SET duration` et indiquer une durée spécifique à la note actuelle avec deux points : `do:3` sera une croche.

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

Pour orienter les accords et les groupes vers le bas, ajoutez un `!` après les parenthèses ou les crochets.
À l'intérieur d'un groupe de croches, on peut changer la durée de chaque note pour indiquer des rythmes complexes

Exemple : `[sol la:4 si:4] [la:4 si do+]`

![](/static/beam_durations.png)

## Liaisons (legato)

Les liaisons type _legato_ ou note soutenue s'indiquent en encadrant les deux notes par des accolades `{}` :

- `{fa+! mi+!}` pour un legato du fa au mi aigu
- `{fa | fa}` pour indiquer que la note doit être tenue jusqu'à la mesure d'après

![](/static/slurs.png)

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