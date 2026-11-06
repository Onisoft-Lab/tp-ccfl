# Rapport qualité - prêt de matériel CCFL

## Récapitulatif des anomalies

| Id | Fichier | Colonne | Description | Nb lignes | Part (%) | Traitement |
|---|---|---|---|---:|---:|---|
| a | materiel.csv | toutes | lignes en doublon strict | 7 | 1.91 | Doublons supprimés (première ligne gardée). |
| b | materiel.csv | annee_achat | année d'achat vide | 9 | 2.45 | Laissé vide, pas d'année inventée. |
| c | materiel.csv | annee_achat | année d'achat postérieure à l'année courante | 5 | 1.36 | Passé en vide (2031 n'est pas crédible). |
| d | materiel.csv | valeur_achat | valeur d'achat vide | 11 | 3.00 | Laissé vide (un 0 fausserait la valeur du parc). |
| e | materiel.csv | categorie | catégorie écrite intégralement en majuscules | 6 | 1.63 | strip + capitalize pour coller aux 6 libellés du service. |
| f | materiel.csv | categorie | catégorie avec espaces en début ou fin | 5 | 1.36 | Espaces enlevés, puis même normalisation que e. |
| g | materiel.csv | valeur_achat | valeur d'achat avec virgule décimale | 5 | 1.36 | Virgule remplacée par un point, puis float. |
| h | associations.csv | code_postal | code postal vide | 9 | 4.29 | Laissé vide (pas de CP inventé depuis la commune). |
| i | associations.csv | type_association | type_association valant 'inconnu' | 7 | 3.33 | Gardé tel quel, signalé dans le rapport. |
| j | associations.csv | date_convention | date_convention au format JJ/MM/AAAA | 6 | 2.86 | Converti en AAAA-MM-JJ. |
| k | reservations.csv | toutes | lignes en doublon strict | 18 | 0.39 | Doublons supprimés (première ligne gardée). |
| l | reservations.csv | id_materiel | id_materiel sans matériel correspondant | 21 | 0.45 | Lignes retirées (sinon la clé étrangère cassera). |
| m | reservations.csv | date_retour_reelle / date_debut | date_retour_reelle antérieure à date_debut | 15 | 0.32 | Lignes retirées (retour avant le début). |
| n | reservations.csv | quantite | quantité égale à zéro | 6 | 0.13 | Lignes retirées (quantité 0 inutile). |

## Effectifs avant / après

- materiel : 367 -> 360
- associations : 210 -> 210
- reservations : 4618 -> 4560

## Prêts en cours

Avant : 72. Après : 71.

Il en manque 1 parce qu'un prêt encore ouvert pointait vers un matériel absent (anomalie l). Les autres prêts sans date de retour sont restés.

## Points d'attention pour la direction

Les catégories sont saisies n'importe comment selon les pôles (majuscules, espaces). Une fois nettoyées, on retombe sur les six familles prévues. Les exports bruts de l'ancien outil ne sont donc pas exploitables tels quels.

Cinq matériels ont une année d'achat en 2031. Erreur de frappe ou mauvais import, difficile à dire. J'ai vidé ces années pour ne pas fausser l'âge du parc.

21 réservations concernent un id_materiel qui n'existe pas (souvent 9999). À vérifier côté métier : reprise manuelle 2024, ou matériel radié trop tôt.

Les prêts sans date de retour, je les ai gardés. Ce sont des prêts en cours. Les sortir fausserait le stock disponible.

Quelques associations n'ont pas de code postal, et d'autres ont le type `inconnu`. Ça passe pour le prêt au quotidien, mais les stats par commune ou par type seront bancales.
