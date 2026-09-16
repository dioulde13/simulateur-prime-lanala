"""Tests unitaires — couvrent les 9 cas de test du cahier des charges
(section 8) plus quelques cas limites directement liés aux règles de gestion
(section 5). À exécuter avec : python -m unittest tests_calcul.py
"""

import unittest
from datetime import date

from core.calcul import ErreurValidation, calculer_palier, simuler
from core.taux_data import GARANTIE_FONCTIONNAIRE, GARANTIE_LES_DEUX, GARANTIE_PERTE_EMPLOI

AUJOURDHUI = date(2024, 1, 1)


def naissance_pour_age(age, aujourdhui=AUJOURDHUI):
    """Date de naissance donnant exactement `age` ans révolus à `aujourdhui`
    (anniversaire déjà passé cette année-là)."""
    return date(aujourdhui.year - age, 1, 1)


class TestCasDuCahierDesCharges(unittest.TestCase):
    def test_01_les_deux_garanties_5_millions_50_mois_36_ans(self):
        resultat = simuler(
            garantie=GARANTIE_LES_DEUX,
            date_naissance=naissance_pour_age(36),
            montant=5_000_000,
            duree=50,
            aujourdhui=AUJOURDHUI,
        )
        self.assertEqual(resultat["palier"], 60)

        details_par_garantie = {d["garantie"]: d for d in resultat["details"]}
        self.assertAlmostEqual(details_par_garantie[GARANTIE_FONCTIONNAIRE]["taux"], 1.52)
        self.assertEqual(details_par_garantie[GARANTIE_FONCTIONNAIRE]["montant"], 76_000)
        self.assertAlmostEqual(details_par_garantie[GARANTIE_PERTE_EMPLOI]["taux"], 1.56)
        self.assertEqual(details_par_garantie[GARANTIE_PERTE_EMPLOI]["montant"], 78_000)

        self.assertEqual(resultat["total"], 154_000)

    def test_02_duree_12_mois_exact_pas_darrondi(self):
        self.assertEqual(calculer_palier(12), 12)

    def test_03_duree_13_mois_palier_24(self):
        self.assertEqual(calculer_palier(13), 24)

    def test_04_duree_240_mois_maximum(self):
        resultat = simuler(
            garantie=GARANTIE_FONCTIONNAIRE,
            date_naissance=naissance_pour_age(40),
            montant=1_000_000,
            duree=240,
            aujourdhui=AUJOURDHUI,
        )
        self.assertEqual(resultat["palier"], 240)
        self.assertEqual(resultat["details"][0]["montant"], round(1_000_000 * 10.22 / 100))

    def test_05_duree_241_mois_erreur(self):
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=GARANTIE_FONCTIONNAIRE,
                date_naissance=naissance_pour_age(40),
                montant=1_000_000,
                duree=241,
                aujourdhui=AUJOURDHUI,
            )
        self.assertEqual(str(ctx.exception), "La durée doit être comprise entre 1 et 240 mois.")

    def test_06_duree_zero_ou_negative_erreur(self):
        for duree_invalide in (0, -5):
            with self.assertRaises(ErreurValidation):
                simuler(
                    garantie=GARANTIE_FONCTIONNAIRE,
                    date_naissance=naissance_pour_age(40),
                    montant=1_000_000,
                    duree=duree_invalide,
                    aujourdhui=AUJOURDHUI,
                )

    def test_07_age_17_ans_mineur_erreur_pas_de_resultat_a_zero(self):
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=GARANTIE_FONCTIONNAIRE,
                date_naissance=naissance_pour_age(17),
                montant=1_000_000,
                duree=60,
                aujourdhui=AUJOURDHUI,
            )
        self.assertIn("Aucun tarif disponible", str(ctx.exception))

    def test_08_age_66_ans_erreur(self):
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=GARANTIE_FONCTIONNAIRE,
                date_naissance=naissance_pour_age(66),
                montant=1_000_000,
                duree=60,
                aujourdhui=AUJOURDHUI,
            )
        self.assertIn("Aucun tarif disponible", str(ctx.exception))

    def test_09_date_naissance_demain_erreur(self):
        demain = date(AUJOURDHUI.year, AUJOURDHUI.month, AUJOURDHUI.day + 1)
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=GARANTIE_FONCTIONNAIRE,
                date_naissance=demain,
                montant=1_000_000,
                duree=60,
                aujourdhui=AUJOURDHUI,
            )
        self.assertEqual(
            str(ctx.exception),
            "La date de naissance ne peut pas être postérieure à aujourd'hui.",
        )


class TestReglesDeGestionComplementaires(unittest.TestCase):
    def test_garantie_non_selectionnee(self):
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=None,
                date_naissance=naissance_pour_age(30),
                montant=1_000_000,
                duree=60,
                aujourdhui=AUJOURDHUI,
            )
        self.assertEqual(str(ctx.exception), "Veuillez sélectionner une garantie.")

    def test_date_naissance_manquante(self):
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=GARANTIE_FONCTIONNAIRE,
                date_naissance=None,
                montant=1_000_000,
                duree=60,
                aujourdhui=AUJOURDHUI,
            )
        self.assertEqual(str(ctx.exception), "Veuillez saisir la date de naissance.")

    def test_montant_manquant_ou_negatif(self):
        for montant_invalide in (None, 0, -100):
            with self.assertRaises(ErreurValidation) as ctx:
                simuler(
                    garantie=GARANTIE_FONCTIONNAIRE,
                    date_naissance=naissance_pour_age(30),
                    montant=montant_invalide,
                    duree=60,
                    aujourdhui=AUJOURDHUI,
                )
            self.assertEqual(
                str(ctx.exception), "Veuillez saisir un montant de prêt supérieur à 0."
            )

    def test_duree_manquante(self):
        with self.assertRaises(ErreurValidation) as ctx:
            simuler(
                garantie=GARANTIE_FONCTIONNAIRE,
                date_naissance=naissance_pour_age(30),
                montant=1_000_000,
                duree=None,
                aujourdhui=AUJOURDHUI,
            )
        self.assertEqual(str(ctx.exception), "Veuillez saisir la durée de remboursement.")

    def test_prime_jamais_divisee_par_la_duree(self):
        resultat = simuler(
            garantie=GARANTIE_FONCTIONNAIRE,
            date_naissance=naissance_pour_age(30),
            montant=1_200_000,
            duree=12,
            aujourdhui=AUJOURDHUI,
        )
        # 1 200 000 x 0.25% = 3000, jamais divisé par 12.
        self.assertEqual(resultat["details"][0]["montant"], 3_000)

    def test_les_deux_ne_produit_jamais_de_resultat_partiel(self):
        # Cas théorique : les deux tables couvrent la même tranche 18-65, donc
        # on vérifie simplement qu'un échec sur une garantie ne laisse aucune
        # clé "details" partiellement remplie visible à l'appelant.
        with self.assertRaises(ErreurValidation):
            simuler(
                garantie=GARANTIE_LES_DEUX,
                date_naissance=naissance_pour_age(70),
                montant=1_000_000,
                duree=60,
                aujourdhui=AUJOURDHUI,
            )


if __name__ == "__main__":
    unittest.main()
