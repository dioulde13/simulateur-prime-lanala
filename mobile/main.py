"""Application Android (Kivy) du simulateur de prime — 100% hors ligne.

Réutilise telle quelle la logique métier de `core/` (calcul.py, taux_data.py),
partagée avec la version desktop. Ce fichier ne contient que l'interface :
aucune règle de gestion n'est dupliquée ici.
"""

from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from core.calcul import MESSAGES, ErreurValidation, simuler
from core.taux_data import GARANTIE_FONCTIONNAIRE, GARANTIE_LES_DEUX, GARANTIE_PERTE_EMPLOI

LIBELLE_A_ID_GARANTIE = {
    "Fonctionnaire": GARANTIE_FONCTIONNAIRE,
    "Perte d'emploi": GARANTIE_PERTE_EMPLOI,
    "Les deux": GARANTIE_LES_DEUX,
}

COULEUR_PRIMAIRE = (0.07, 0.24, 0.41, 1)
COULEUR_ACCENT = (0.10, 0.48, 0.24, 1)
COULEUR_TEXTE = (0.12, 0.16, 0.20, 1)
COULEUR_MUTE = (0.35, 0.39, 0.45, 1)


def _formater_montant(valeur):
    return f"{valeur:,}".replace(",", " ")


def _champ_label(texte):
    return Label(
        text=texte,
        color=COULEUR_TEXTE,
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(28),
    )


class SimulateurLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(12), **kwargs)

        self.add_widget(
            Label(
                text="Simulateur de prime — Lanala Bank",
                font_size=dp(20),
                bold=True,
                color=COULEUR_PRIMAIRE,
                size_hint_y=None,
                height=dp(40),
            )
        )

        formulaire = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        formulaire.bind(minimum_height=formulaire.setter("height"))

        formulaire.add_widget(_champ_label("Garantie *"))
        self.spinner_garantie = Spinner(
            text="Sélectionner",
            values=list(LIBELLE_A_ID_GARANTIE.keys()),
            size_hint_y=None,
            height=dp(44),
        )
        formulaire.add_widget(self.spinner_garantie)

        formulaire.add_widget(_champ_label("Date de naissance (JJ/MM/AAAA) *"))
        self.champ_date = TextInput(
            hint_text="JJ/MM/AAAA",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            input_type="number",
        )
        formulaire.add_widget(self.champ_date)

        formulaire.add_widget(_champ_label("Montant du prêt *"))
        self.champ_montant = TextInput(
            hint_text="Ex. 2000000",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(44),
            input_type="number",
        )
        formulaire.add_widget(self.champ_montant)

        formulaire.add_widget(_champ_label("Durée de remboursement (mois) *"))
        self.champ_duree = TextInput(
            hint_text="Ex. 60",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(44),
            input_type="number",
        )
        formulaire.add_widget(self.champ_duree)

        self.add_widget(formulaire)

        boutons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        bouton_simuler = Button(text="Simuler", bold=True, background_color=COULEUR_PRIMAIRE)
        bouton_simuler.bind(on_release=self._on_simuler)
        bouton_reset = Button(text="Réinitialiser")
        bouton_reset.bind(on_release=self._on_reinitialiser)
        boutons.add_widget(bouton_simuler)
        boutons.add_widget(bouton_reset)
        self.add_widget(boutons)

        self.zone_resultat = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.zone_resultat.bind(minimum_height=self.zone_resultat.setter("height"))

        defilement = ScrollView()
        defilement.add_widget(self.zone_resultat)
        self.add_widget(defilement)

    def _lire_date_naissance(self):
        texte = self.champ_date.text.strip()
        if not texte:
            return None
        try:
            return datetime.strptime(texte, "%d/%m/%Y").date()
        except ValueError:
            raise ErreurValidation("Format de date invalide. Utilisez JJ/MM/AAAA.")

    def _lire_entier(self, texte, message_si_invalide):
        texte = texte.strip()
        if not texte:
            return None
        try:
            return int(texte)
        except ValueError:
            raise ErreurValidation(message_si_invalide)

    def _afficher_erreur(self, message):
        Popup(
            title="Erreur de saisie",
            content=Label(text=message, color=COULEUR_TEXTE),
            size_hint=(0.85, 0.35),
        ).open()

    def _on_simuler(self, *_args):
        try:
            garantie = LIBELLE_A_ID_GARANTIE.get(self.spinner_garantie.text)
            if garantie is None:
                raise ErreurValidation(MESSAGES["garantie_manquante"])

            date_naissance = self._lire_date_naissance()
            montant = self._lire_entier(self.champ_montant.text, MESSAGES["montant_invalide"])
            duree = self._lire_entier(self.champ_duree.text, MESSAGES["duree_hors_plage"])

            resultat = simuler(garantie, date_naissance, montant, duree)
        except ErreurValidation as erreur:
            self.zone_resultat.clear_widgets()
            self._afficher_erreur(str(erreur))
            return

        self._afficher_resultat(resultat)

    def _afficher_resultat(self, resultat):
        self.zone_resultat.clear_widgets()

        self.zone_resultat.add_widget(
            _champ_label(f"Âge calculé : {resultat['age']} ans")
        )

        if resultat["duree_saisie"] != resultat["palier"]:
            texte_duree = (
                f"Durée saisie : {resultat['duree_saisie']} mois "
                f"— tarifée sur {resultat['palier']} mois"
            )
        else:
            texte_duree = f"Durée : {resultat['palier']} mois"
        self.zone_resultat.add_widget(_champ_label(texte_duree))

        self.zone_resultat.add_widget(
            Label(
                text="Détail par garantie",
                bold=True,
                color=COULEUR_PRIMAIRE,
                size_hint_y=None,
                height=dp(30),
            )
        )
        for detail in resultat["details"]:
            texte = (
                f"{detail['libelle']} — taux {detail['taux']:.2f} % "
                f"— prime : {_formater_montant(detail['montant'])}"
            )
            self.zone_resultat.add_widget(_champ_label(texte))

        self.zone_resultat.add_widget(
            Label(
                text=f"Prime totale : {_formater_montant(resultat['total'])}",
                bold=True,
                font_size=dp(22),
                color=COULEUR_ACCENT,
                size_hint_y=None,
                height=dp(48),
            )
        )

    def _on_reinitialiser(self, *_args):
        self.spinner_garantie.text = "Sélectionner"
        self.champ_date.text = ""
        self.champ_montant.text = ""
        self.champ_duree.text = ""
        self.zone_resultat.clear_widgets()


class SimulateurPrimeApp(App):
    title = "Simulateur de prime — Lanala Bank"

    def build(self):
        return SimulateurLayout()


if __name__ == "__main__":
    SimulateurPrimeApp().run()
