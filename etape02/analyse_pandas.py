# Étape 2 : pandas (typage, agrégats, merge)

from __future__ import annotations

from pathlib import Path

import pandas as pd

CHEMIN_SITES = Path("data/sites.csv")
CHEMIN_MATERIEL = Path("data/materiel.csv")
CHEMIN_ASSOCIATIONS = Path("data/associations.csv")
CHEMIN_RESERVATIONS = Path("data/reservations.csv")
CHEMIN_TOP10 = Path("sorties/top10_materiel.csv")


def charger_donnees() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_sites = pd.read_csv(CHEMIN_SITES)
    df_materiel = pd.read_csv(CHEMIN_MATERIEL)
    df_associations = pd.read_csv(CHEMIN_ASSOCIATIONS)
    df_reservations = pd.read_csv(CHEMIN_RESERVATIONS)

    for col in ("date_debut", "date_fin_prevue", "date_retour_reelle"):
        df_reservations[col] = pd.to_datetime(df_reservations[col], errors="coerce")

    # certains montants sont écrits avec une virgule (ex: 180,08)
    if not pd.api.types.is_numeric_dtype(df_materiel["valeur_achat"]):
        df_materiel["valeur_achat"] = pd.to_numeric(
            df_materiel["valeur_achat"].astype(str).str.replace(",", ".", regex=False),
            errors="coerce",
        )

    return df_sites, df_materiel, df_associations, df_reservations


def afficher_apercu(nom: str, df: pd.DataFrame) -> None:
    print(f"\n=== {nom} ===")
    print(f"shape : {df.shape}")
    print("info :")
    df.info()
    print("valeurs manquantes :")
    print(df.isna().sum())


def main() -> None:
    df_sites, df_materiel, df_associations, df_reservations = charger_donnees()

    afficher_apercu("df_materiel", df_materiel)
    afficher_apercu("df_reservations", df_reservations)

    print("\n10 matériels les plus chers :")
    top_chers = (
        df_materiel[["reference", "designation", "categorie", "valeur_achat"]]
        .sort_values("valeur_achat", ascending=False)
        .head(10)
    )
    print(top_chers.to_string(index=False))

    print("\nNombre de matériels par categorie :")
    print(df_materiel["categorie"].value_counts())

    print("\nRéservations et quantité par code_site :")
    par_site = (
        df_reservations.groupby("code_site")
        .agg(nb=("id_reservation", "size"), quantite=("quantite", "sum"))
        .sort_values("nb", ascending=False)
    )
    print(par_site)

    # sans ça, les id_materiel en double multiplient les lignes au merge
    materiel_unique = df_materiel.drop_duplicates(subset=["id_materiel"])
    df_complet = df_reservations.merge(
        materiel_unique, on="id_materiel", how="left", suffixes=("", "_mat")
    ).merge(
        df_associations, on="id_association", how="left", suffixes=("", "_asso")
    )

    sans_materiel = df_complet["designation"].isna().sum()
    print(f"\nLignes de df_complet : {len(df_complet)}")
    print(f"Lignes sans matériel correspondant : {sans_materiel}")

    top10 = (
        df_complet.dropna(subset=["designation"])
        .groupby(["id_materiel", "designation"], as_index=False)
        .size()
        .rename(columns={"size": "nb_reservations"})
        .sort_values("nb_reservations", ascending=False)
        .head(10)
    )
    print("\nTop 10 matériels les plus réservés :")
    print(top10.to_string(index=False))

    CHEMIN_TOP10.parent.mkdir(parents=True, exist_ok=True)
    top10.to_csv(CHEMIN_TOP10, index=False, encoding="utf-8")
    print(f"\nExport : {CHEMIN_TOP10}")


if __name__ == "__main__":
    main()
