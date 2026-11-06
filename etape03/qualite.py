# Étape 3 : détection des anomalies, nettoyage, rapport

from __future__ import annotations

from pathlib import Path

import pandas as pd

CHEMIN_MATERIEL = Path("data/materiel.csv")
CHEMIN_ASSOCIATIONS = Path("data/associations.csv")
CHEMIN_RESERVATIONS = Path("data/reservations.csv")

SORTIE_MAT = Path("sorties/materiel_propre.csv")
SORTIE_ASSO = Path("sorties/associations_propre.csv")
SORTIE_RES = Path("sorties/reservations_propre.csv")
SORTIE_RAPPORT = Path("sorties/rapport_qualite.md")

ANNEE_COURANTE = 2026


def _echantillon(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    return df.head(n)


def detecter() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    materiel = pd.read_csv(CHEMIN_MATERIEL, dtype=str)
    associations = pd.read_csv(CHEMIN_ASSOCIATIONS, dtype=str)
    reservations = pd.read_csv(CHEMIN_RESERVATIONS, dtype=str)

    annee_num = pd.to_numeric(materiel["annee_achat"], errors="coerce")

    anomalies = {
        "a": {
            "fichier": "materiel.csv",
            "colonne": "toutes",
            "description": "lignes en doublon strict",
            "masque": materiel.duplicated(keep="first"),
            "traitement": "Doublons supprimés (première ligne gardée).",
        },
        "b": {
            "fichier": "materiel.csv",
            "colonne": "annee_achat",
            "description": "année d'achat vide",
            "masque": materiel["annee_achat"].fillna("").str.strip().eq(""),
            "traitement": "Laissé vide, pas d'année inventée.",
        },
        "c": {
            "fichier": "materiel.csv",
            "colonne": "annee_achat",
            "description": "année d'achat postérieure à l'année courante",
            "masque": annee_num.gt(ANNEE_COURANTE).fillna(False),
            "traitement": "Passé en vide (2031 n'est pas crédible).",
        },
        "d": {
            "fichier": "materiel.csv",
            "colonne": "valeur_achat",
            "description": "valeur d'achat vide",
            "masque": materiel["valeur_achat"].fillna("").str.strip().eq(""),
            "traitement": "Laissé vide (un 0 fausserait la valeur du parc).",
        },
        "e": {
            "fichier": "materiel.csv",
            "colonne": "categorie",
            "description": "catégorie écrite intégralement en majuscules",
            "masque": materiel["categorie"]
            .fillna("")
            .str.strip()
            .str.isupper()
            .fillna(False),
            "traitement": "strip + capitalize pour coller aux 6 libellés du service.",
        },
        "f": {
            "fichier": "materiel.csv",
            "colonne": "categorie",
            "description": "catégorie avec espaces en début ou fin",
            "masque": materiel["categorie"].ne(materiel["categorie"].str.strip()),
            "traitement": "Espaces enlevés, puis même normalisation que e.",
        },
        "g": {
            "fichier": "materiel.csv",
            "colonne": "valeur_achat",
            "description": "valeur d'achat avec virgule décimale",
            "masque": materiel["valeur_achat"].fillna("").str.contains(","),
            "traitement": "Virgule remplacée par un point, puis float.",
        },
        "h": {
            "fichier": "associations.csv",
            "colonne": "code_postal",
            "description": "code postal vide",
            "masque": associations["code_postal"].fillna("").str.strip().eq(""),
            "traitement": "Laissé vide (pas de CP inventé depuis la commune).",
        },
        "i": {
            "fichier": "associations.csv",
            "colonne": "type_association",
            "description": "type_association valant 'inconnu'",
            "masque": associations["type_association"].eq("inconnu"),
            "traitement": "Gardé tel quel, signalé dans le rapport.",
        },
        "j": {
            "fichier": "associations.csv",
            "colonne": "date_convention",
            "description": "date_convention au format JJ/MM/AAAA",
            "masque": associations["date_convention"]
            .fillna("")
            .str.match(r"^\d{2}/\d{2}/\d{4}$"),
            "traitement": "Converti en AAAA-MM-JJ.",
        },
        "k": {
            "fichier": "reservations.csv",
            "colonne": "toutes",
            "description": "lignes en doublon strict",
            "masque": reservations.duplicated(keep="first"),
            "traitement": "Doublons supprimés (première ligne gardée).",
        },
        "l": {
            "fichier": "reservations.csv",
            "colonne": "id_materiel",
            "description": "id_materiel sans matériel correspondant",
            "masque": ~reservations["id_materiel"].isin(materiel["id_materiel"]),
            "traitement": "Lignes retirées (sinon la clé étrangère cassera).",
        },
        "m": {
            "fichier": "reservations.csv",
            "colonne": "date_retour_reelle / date_debut",
            "description": "date_retour_reelle antérieure à date_debut",
            "masque": _chrono_impossible(reservations),
            "traitement": "Lignes retirées (retour avant le début).",
        },
        "n": {
            "fichier": "reservations.csv",
            "colonne": "quantite",
            "description": "quantité égale à zéro",
            "masque": pd.to_numeric(reservations["quantite"], errors="coerce").eq(0),
            "traitement": "Lignes retirées (quantité 0 inutile).",
        },
    }

    return anomalies, materiel, associations, reservations


def _chrono_impossible(reservations: pd.DataFrame) -> pd.Series:
    debut = pd.to_datetime(reservations["date_debut"], errors="coerce")
    retour = pd.to_datetime(reservations["date_retour_reelle"], errors="coerce")
    return retour.notna() & (retour < debut)


def nettoyer(
    materiel: pd.DataFrame,
    associations: pd.DataFrame,
    reservations: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mat = materiel.drop_duplicates().copy()
    mat["categorie"] = mat["categorie"].str.strip().str.capitalize()

    annee = pd.to_numeric(mat["annee_achat"], errors="coerce")
    annee = annee.where(~annee.gt(ANNEE_COURANTE))
    mat["annee_achat"] = annee.apply(
        lambda x: "" if pd.isna(x) else str(int(x))
    )

    valeur = (
        mat["valeur_achat"]
        .fillna("")
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    valeur_num = pd.to_numeric(valeur.replace("", pd.NA), errors="coerce")
    mat["valeur_achat"] = valeur_num

    asso = associations.copy()
    iso = pd.to_datetime(asso["date_convention"], format="%Y-%m-%d", errors="coerce")
    fr = pd.to_datetime(asso["date_convention"], format="%d/%m/%Y", errors="coerce")
    asso["date_convention"] = iso.fillna(fr).dt.strftime("%Y-%m-%d")

    res = reservations.drop_duplicates().copy()
    res = res[res["id_materiel"].isin(mat["id_materiel"])].copy()
    res = res[~_chrono_impossible(res)].copy()
    res = res[pd.to_numeric(res["quantite"], errors="coerce").ne(0)].copy()

    mat["id_materiel"] = pd.to_numeric(mat["id_materiel"], errors="coerce").astype("Int64")
    for col in ("id_materiel", "id_association", "quantite"):
        res[col] = pd.to_numeric(res[col], errors="coerce").astype("Int64")
    asso["id_association"] = pd.to_numeric(asso["id_association"], errors="coerce").astype(
        "Int64"
    )

    return mat, asso, res


def pret_en_cours(df: pd.DataFrame) -> int:
    return (
        df["date_retour_reelle"].isna().sum()
        if pd.api.types.is_datetime64_any_dtype(df["date_retour_reelle"])
        else df["date_retour_reelle"].fillna("").astype(str).str.strip().eq("").sum()
    )


def ecrire_rapport(
    anomalies: dict,
    frames: dict[str, pd.DataFrame],
    propres: dict[str, pd.DataFrame],
    nb_cours_avant: int,
    nb_cours_apres: int,
) -> str:
    lignes = [
        "# Rapport qualité - prêt de matériel CCFL",
        "",
        "## Récapitulatif des anomalies",
        "",
        "| Id | Fichier | Colonne | Description | Nb lignes | Part (%) | Traitement |",
        "|---|---|---|---|---:|---:|---|",
    ]

    tailles = {
        "materiel.csv": len(frames["materiel"]),
        "associations.csv": len(frames["associations"]),
        "reservations.csv": len(frames["reservations"]),
    }

    for cle, info in anomalies.items():
        n = int(info["masque"].sum())
        total = tailles[info["fichier"]]
        part = 100.0 * n / total if total else 0.0
        lignes.append(
            f"| {cle} | {info['fichier']} | {info['colonne']} | "
            f"{info['description']} | {n} | {part:.2f} | {info['traitement']} |"
        )

    n_mat_b, n_mat_a = len(frames["materiel"]), len(propres["materiel"])
    n_asso_b, n_asso_a = len(frames["associations"]), len(propres["associations"])
    n_res_b, n_res_a = len(frames["reservations"]), len(propres["reservations"])

    lignes.extend(
        [
            "",
            "## Effectifs avant / après",
            "",
            f"- materiel : {n_mat_b} -> {n_mat_a}",
            f"- associations : {n_asso_b} -> {n_asso_a}",
            f"- reservations : {n_res_b} -> {n_res_a}",
            "",
            "## Prêts en cours",
            "",
            f"Avant : {nb_cours_avant}. Après : {nb_cours_apres}.",
            "",
            (
                f"Il en manque {nb_cours_avant - nb_cours_apres} parce qu'un prêt "
                "encore ouvert pointait vers un matériel absent (anomalie l). "
                "Les autres prêts sans date de retour sont restés."
            ),
            "",
            "## Points d'attention pour la direction",
            "",
            (
                "Les catégories sont saisies n'importe comment selon les pôles "
                "(majuscules, espaces). Une fois nettoyées, on retombe sur les "
                "six familles prévues. Les exports bruts de l'ancien outil ne "
                "sont donc pas exploitables tels quels."
            ),
            "",
            (
                "Cinq matériels ont une année d'achat en 2031. Erreur de frappe "
                "ou mauvais import, difficile à dire. J'ai vidé ces années pour "
                "ne pas fausser l'âge du parc."
            ),
            "",
            (
                "21 réservations concernent un id_materiel qui n'existe pas "
                "(souvent 9999). À vérifier côté métier : reprise manuelle 2024, "
                "ou matériel radié trop tôt."
            ),
            "",
            (
                "Les prêts sans date de retour, je les ai gardés. Ce sont des "
                "prêts en cours. Les sortir fausserait le stock disponible."
            ),
            "",
            (
                "Quelques associations n'ont pas de code postal, et d'autres ont "
                "le type `inconnu`. Ça passe pour le prêt au quotidien, mais les "
                "stats par commune ou par type seront bancales."
            ),
            "",
        ]
    )
    return "\n".join(lignes)


def main() -> None:
    anomalies, materiel, associations, reservations = detecter()

    print("=== Detection ===")
    for cle, info in anomalies.items():
        n = int(info["masque"].sum())
        print(f"[{cle}] {info['description']} : {n}")
        if n:
            print(_echantillon(frames_from(info, materiel, associations, reservations)))

    nb_cours_avant = pret_en_cours(reservations)
    mat_p, asso_p, res_p = nettoyer(materiel, associations, reservations)
    nb_cours_apres = pret_en_cours(res_p)

    for chemin, df in (
        (SORTIE_MAT, mat_p),
        (SORTIE_ASSO, asso_p),
        (SORTIE_RES, res_p),
    ):
        chemin.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(chemin, index=False, encoding="utf-8")

    rapport = ecrire_rapport(
        anomalies,
        {
            "materiel": materiel,
            "associations": associations,
            "reservations": reservations,
        },
        {
            "materiel": mat_p,
            "associations": asso_p,
            "reservations": res_p,
        },
        nb_cours_avant,
        nb_cours_apres,
    )
    SORTIE_RAPPORT.write_text(rapport, encoding="utf-8")

    print("\n=== Controles ===")
    print(f"materiel propre : {len(mat_p)} lignes, {mat_p['categorie'].nunique()} categories")
    print(f"reservations propres : {len(res_p)}")
    print(f"prets en cours : {nb_cours_avant} -> {nb_cours_apres}")
    print(f"Rapport : {SORTIE_RAPPORT}")


def frames_from(info: dict, materiel, associations, reservations) -> pd.DataFrame:
    mapping = {
        "materiel.csv": materiel,
        "associations.csv": associations,
        "reservations.csv": reservations,
    }
    return mapping[info["fichier"]].loc[info["masque"]]


if __name__ == "__main__":
    main()
