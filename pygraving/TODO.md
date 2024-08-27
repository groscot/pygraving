# TODO

## features musicales

- [x] symboles pour les silences: importer
- [ ] symboles pour les silences: intégrer
- [-] gérer les time signatures différentes
- [x] beamed group: refactorer pour vraiment utiliser l'api Notes (compatible avec alterations etc.)
- [ ] liés (arcs en haut des notes) <- la syntaxe va pas être évidente, peut etre utiliser "PLACE slur"
- [x] répétitions blocs
- [ ] ajouter une logique de mesure


## cohérence générale

- [x] arranger chord pour pouvoir donner des altérations aux notes
- [ ] note pointee : la duree (pos auto) doit etre ajustee
- [ ] note pointee : positionnement à revoir
- [ ] lignes multiples : comment garantir que les mesures correspondent ?
- [x] corriger les traits verticaux : pas à gauche, et à droite sans depassement apres
- [x] chord: notes qui se superposent


## automatic layout

- [ ] probleme de marge si: les notes extremes ont des alterations, ou si derniere note pointee, ou avec beamed group
- [ ] probablement vaut le coup de refactorer la logique (GROS TRUC)
- [ ] contraindre spacing par le voice track


## features quality of life

- [ ] mode debug qui affiche les positions etc