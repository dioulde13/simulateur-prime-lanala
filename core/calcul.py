"""Logique métier pure du simulateur de prime (cahier des charges, section 4).

Ce module ne dépend d'aucune bibliothèque graphique (pas d'import tkinter) et
n'effectue aucun appel réseau : il est testable isolément (voir
tests_calcul.py) et réutilisable tel quel sur toutes les plateformes cibles
(desktop, Android, web).
"""

import math
from datetime import date

from .taux_data import (
    DUREE_MAX,
    GARANTIE_FONCTIONNAIRE,
    GARANTIE_LES_DEUX,
    GARANTIE_PERTE_EMPLOI,
    GARANTIES_VALIDES,
    LIBELLES_GARANTIE,
    chercher_taux,
)

# Messages utilisateur exacts (cahier des charges, section 7).
MESSAGES = {
    "garantie_manquante": "Veuillez sélectionner une garantie.",
    "date_manquante": "Veuillez saisir la date de naissance.",
    "date_future": "La date de naissance ne peut pas être postérieure à aujourd'hui.",
    "montant_invalide": "Veuillez saisir un montant de prêt supérieur à 0.",
    "duree_manquante": "Veuillez saisir la durée de remboursement.",
    "duree_hors_plage": "La durée doit être comprise entre 1 et 240 mois.",
    "age_hors_tranche": (
        "Aucun tarif disponible pour cet âge (tarification réservée aux 18-65 ans)."
    ),
}


class ErreurValidation(Exception):
    """Erreur de saisie ou d'éligibilité — porte le message à afficher tel quel."""


def calculer_age(date_naissance, aujourdhui):
    """Nombre d'années révolues entre `date_naissance` et `aujourdhui`."""
    age = aujourdhui.year - date_naissance.year
    if (aujourdhui.month, aujourdhui.day) < (date_naissance.month, date_naissance.day):
        age -= 1
    return age


def calculer_palier(duree):
    """Arrondit `duree` (en mois) au multiple de 12 immédiatement supérieur.

    Lève ErreurValidation si `duree` est hors de la plage 1-240 (cahier des
    charges, section 5 : « 241 mois et plus, ou <= 0 -> erreur, pas de calcul »).
    """
    if duree is None or duree <= 0 or duree > DUREE_MAX:
        raise ErreurValidation(MESSAGES["duree_hors_plage"])
    return math.ceil(duree / 12) * 12


def garanties_a_calculer(garantie):
    """Une seule garantie, sauf « Les deux » qui déclenche les deux calculs."""
    if garantie == GARANTIE_LES_DEUX:
        return [GARANTIE_FONCTIONNAIRE, GARANTIE_PERTE_EMPLOI]
    return [garantie]


def _arrondir_entier_le_plus_proche(valeur):
    """Arrondi classique (moitié vers le haut), pour éviter les surprises du
    'banker's rounding' de la fonction round() native de Python sur les .5."""
    return int(math.floor(valeur + 0.5))


def valider_entrees(garantie, date_naissance, montant, duree, aujourdhui):
    """Valide individuellement les 4 champs (section 2) et lève
    ErreurValidation avec le message correspondant au premier problème trouvé."""
    if not garantie or garantie not in GARANTIES_VALIDES:
        raise ErreurValidation(MESSAGES["garantie_manquante"])

    if date_naissance is None:
        raise ErreurValidation(MESSAGES["date_manquante"])
    if date_naissance > aujourdhui:
        raise ErreurValidation(MESSAGES["date_future"])

    if montant is None or montant <= 0:
        raise ErreurValidation(MESSAGES["montant_invalide"])

    if duree is None:
        raise ErreurValidation(MESSAGES["duree_manquante"])
    if duree <= 0 or duree > DUREE_MAX:
        raise ErreurValidation(MESSAGES["duree_hors_plage"])


def simuler(garantie, date_naissance, montant, duree, aujourdhui=None):
    """Exécute l'algorithme complet (section 4) et retourne un dict résultat :

    {
        "age": int,
        "duree_saisie": int,
        "palier": int,
        "details": [{"garantie": id, "libelle": str, "taux": float, "montant": int}, ...],
        "total": int,
    }

    Lève ErreurValidation (avec le message à afficher tel quel) dès qu'une
    règle du cahier des charges n'est pas respectée ; dans ce cas, aucun
    résultat partiel n'est retourné.
    """
    if aujourdhui is None:
        aujourdhui = date.today()

    valider_entrees(garantie, date_naissance, montant, duree, aujourdhui)

    age = calculer_age(date_naissance, aujourdhui)
    palier = calculer_palier(duree)

    details = []
    for garantie_id in garanties_a_calculer(garantie):
        taux = chercher_taux(garantie_id, age, palier)
        if taux is None:
            # Age hors tranche 18-65 : échec total, pas de résultat partiel,
            # même si l'autre garantie (cas "Les deux") aurait un taux valide.
            raise ErreurValidation(MESSAGES["age_hors_tranche"])
        montant_prime = _arrondir_entier_le_plus_proche(montant * taux / 100)
        details.append(
            {
                "garantie": garantie_id,
                "libelle": LIBELLES_GARANTIE[garantie_id],
                "taux": taux,
                "montant": montant_prime,
            }
        )

    total = sum(detail["montant"] for detail in details)

    return {
        "age": age,
        "duree_saisie": duree,
        "palier": palier,
        "details": details,
        "total": total,
    }
