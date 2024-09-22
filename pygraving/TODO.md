# TODO

## features musicales

- [x] symboles pour les silences: importer
- [x] symboles pour les silences: intégrer
- [x] gérer les time signatures différentes
- [x] beamed group: refactorer pour vraiment utiliser l'api Notes (compatible avec alterations etc.)
- [x] répétitions blocs
- [x] liés (arcs en haut des notes) <- la syntaxe va pas être évidente, peut etre utiliser "PLACE slur"
- [ ] ajouter une logique de mesure


## cohérence générale

- [x] arranger chord pour pouvoir donner des altérations aux notes
- [x] note pointee : la duree (pos auto) doit etre ajustee
- [ ] note pointee : positionnement à revoir
- [ ] lignes multiples : comment garantir que les mesures correspondent ?
- [x] corriger les traits verticaux : pas à gauche, et à droite sans depassement apres
- [x] chord: notes qui se superposent


## automatic layout

- [ ] probleme de marge si: les notes extremes ont des alterations, ou si derniere note pointee, ou avec beamed group
- [ ] probleme de marge si: chord do/re (1 d'écart) + silences
- [-] probablement vaut le coup de refactorer la logique (GROS TRUC)
- [ ] contraindre spacing par le voice track


## features quality of life

- [x] mode debug qui affiche les positions etc
- [ ] Gestion de plusieurs pages


# Regex pour migrer [voice] en "voice"

\[([^\[\]]+)\|([^\[\]]+)\]
"$1" "$2"