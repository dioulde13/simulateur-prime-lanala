"""Grille de taux — simulateur de prime d'assurance emprunteur (Lanala Bank).

Grille figée fournie par la banque, recopiée telle quelle (cahier des charges,
section 3). Toute évolution des taux ne doit toucher QUE ce fichier — voir
section 10 du cahier des charges (« Maintenance des taux »).

La tranche d'âge (18-65 ans) est un paramètre explicite de la donnée
(age_min / age_max) et non une hypothèse codée dans la logique de calcul :
cela permet d'ajouter une deuxième tranche d'âge un jour sans réécrire
l'algorithme dans calcul.py.
"""

# Identifiants internes des garanties (jamais traduits, utilisés uniquement
# dans le code). Les libellés affichés à l'utilisateur sont dans
# LIBELLES_GARANTIE ci-dessous.
GARANTIE_FONCTIONNAIRE = "PRIME_FONCTIONNAIRE"
GARANTIE_PERTE_EMPLOI = "PRIME_PERTE_EMPLOI"
GARANTIE_LES_DEUX = "PRIME_FONCTIONNAIRE_ET_PRIME_PERTE_EMPLOI"

GARANTIES_VALIDES = (GARANTIE_FONCTIONNAIRE, GARANTIE_PERTE_EMPLOI, GARANTIE_LES_DEUX)

LIBELLES_GARANTIE = {
    GARANTIE_FONCTIONNAIRE: "Fonctionnaire",
    GARANTIE_PERTE_EMPLOI: "Perte d'emploi",
}

DUREE_MIN = 1
DUREE_MAX = 240
PALIERS = tuple(range(12, DUREE_MAX + 1, 12))  # 12, 24, ..., 240

# Chaque garantie est associée à une LISTE de tranches d'âge. Aujourd'hui une
# seule tranche existe (18-65 ans) ; une deuxième tranche s'ajouterait comme un
# nouvel élément de la liste, sans toucher à calcul.py.
_TAUX_FONCTIONNAIRE_18_65 = {
    "age_min": 18,
    "age_max": 65,
    "taux": {
        12: 0.25,
        24: 0.53,
        36: 0.84,
        48: 1.17,
        60: 1.52,
        72: 1.74,
        84: 2.10,
        96: 2.50,
        108: 2.92,
        120: 3.36,
        132: 3.84,
        144: 4.34,
        156: 4.87,
        168: 5.43,
        180: 6.02,
        192: 7.02,
        204: 7.53,
        216: 9.01,
        228: 10.00,
        240: 10.22,
    },
}

_TAUX_PERTE_EMPLOI_18_65 = {
    "age_min": 18,
    "age_max": 65,
    "taux": {
        12: 0.29,
        24: 0.57,
        36: 0.88,
        48: 1.21,
        60: 1.56,
        72: 3.74,
        84: 4.10,
        96: 4.50,
        108: 4.92,
        120: 5.36,
        132: 5.84,
        144: 6.34,
        156: 6.87,
        168: 7.43,
        180: 8.02,
        192: 8.72,
        204: 9.04,
        216: 10.02,
        228: 11.05,
        240: 12.07,
    },
}

GRILLES_TAUX = {
    GARANTIE_FONCTIONNAIRE: [_TAUX_FONCTIONNAIRE_18_65],
    GARANTIE_PERTE_EMPLOI: [_TAUX_PERTE_EMPLOI_18_65],
}


def chercher_taux(garantie_id, age, palier):
    """Retourne le taux (en %) pour (garantie, âge, palier), ou None si aucune
    tranche d'âge de cette garantie ne couvre `age` — cas d'erreur explicite
    à gérer par l'appelant (jamais un taux par défaut, jamais 0)."""
    for tranche in GRILLES_TAUX.get(garantie_id, []):
        if tranche["age_min"] <= age <= tranche["age_max"]:
            return tranche["taux"].get(palier)
    return None
