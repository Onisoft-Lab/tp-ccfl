# Étape 1 : lecture des CSV sans pandas

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

# Lancer depuis la racine tp-ccfl/
CHEMIN_SITES = Path("data/sites.csv")
CHEMIN_MATERIEL = Path("data/materiel.csv")
CHEMIN_ASSOCIATIONS = Path("data/associations.csv")
CHEMIN_RESERVATIONS = Path("data/reservations.csv")

ANNEE_REFERENCE = 2026


def lire_csv(chemin: str | Path) -> list[dict[str, str]]:
    with open(chemin, encoding="utf-8", newline="") as fichier:
        return list(csv.DictReader(fichier))


def compter_par(lignes: list[dict], colonne: str) -> dict[str, int]:
    return dict(Counter(ligne[colonne] for ligne in lignes))


def total_par(
    lignes: list[dict], colonne_groupe: str, colonne_valeur: str
) -> dict[str, int]:
    totaux: dict[str, int] = {}
    for ligne in lignes:
        cle = ligne[colonne_groupe]
        totaux[cle] = totaux.get(cle, 0) + int(ligne[colonne_valeur])
    return totaux


class Site:
    def __init__(
        self,
        code_site: str,
        nom: str,
        commune: str,
        annee_ouverture: str | int,
        surface_m2: str | int,
    ) -> None:
        self.code_site = code_site
        self.nom = nom
        self.commune = commune
        self.annee_ouverture = int(annee_ouverture)
        self.surface_m2 = int(surface_m2)

    def anciennete(self, annee_reference: int) -> int:
        return annee_reference - self.annee_ouverture

    def __str__(self) -> str:
        return (
            f"{self.code_site} - {self.nom} ({self.commune}), "
            f"{self.surface_m2} m2"
        )


def reservations_en_cours(reservations: list[dict]) -> list[dict]:
    # date_retour_reelle vide = prêt encore ouvert
    return [
        r
        for r in reservations
        if not r["date_retour_reelle"].strip()
    ]


def _tri_desc(dico: dict[str, int]) -> list[tuple[str, int]]:
    return sorted(dico.items(), key=lambda couple: couple[1], reverse=True)


def main() -> None:
    sites = lire_csv(CHEMIN_SITES)
    materiel = lire_csv(CHEMIN_MATERIEL)
    associations = lire_csv(CHEMIN_ASSOCIATIONS)
    reservations = lire_csv(CHEMIN_RESERVATIONS)

    print(f"Nombre de sites : {len(sites)}")
    print(f"Nombre de matériels : {len(materiel)}")
    print(f"Nombre d'associations : {len(associations)}")
    print(f"Nombre de réservations : {len(reservations)}")

    print("\nSites et ancienneté (réf. 2026) :")
    for ligne in sites:
        site = Site(**ligne)
        print(f"  {site} - ancienneté {site.anciennete(ANNEE_REFERENCE)} ans")

    print("\nRéservations par code_site :")
    for code, nb in _tri_desc(compter_par(reservations, "code_site")):
        print(f"  {code} : {nb}")

    print("\nQuantité totale réservée par code_site :")
    for code, total in _tri_desc(
        total_par(reservations, "code_site", "quantite")
    ):
        print(f"  {code} : {total}")

    print("\nMatériels par état :")
    for etat, nb in _tri_desc(compter_par(materiel, "etat")):
        print(f"  {etat} : {nb}")

    categories = {ligne["categorie"] for ligne in materiel}
    print(f"\nValeurs distinctes de categorie : {len(categories)}")

    en_cours = reservations_en_cours(reservations)
    print(f"Réservations en cours : {len(en_cours)}")


if __name__ == "__main__":
    main()
