"""Interface graphique Tkinter du simulateur (100% hors ligne).

Ce module ne contient aucune logique métier : il collecte les 4 champs,
délègue entièrement le calcul à `calcul.simuler`, et affiche soit le résultat
soit le message d'erreur renvoyé. Toute règle de gestion vit dans calcul.py /
taux_data.py, conformément à la recommandation du cahier des charges
(section 10) de garder la table de taux et la logique isolées de l'UI.
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from core.calcul import MESSAGES, ErreurValidation, simuler
from core.taux_data import GARANTIE_FONCTIONNAIRE, GARANTIE_LES_DEUX, GARANTIE_PERTE_EMPLOI

LIBELLE_A_ID_GARANTIE = {
    "Fonctionnaire": GARANTIE_FONCTIONNAIRE,
    "Perte d'emploi": GARANTIE_PERTE_EMPLOI,
    "Les deux": GARANTIE_LES_DEUX,
}

# Palette de couleurs de l'application.
COULEUR_PRIMAIRE = "#123C69"
COULEUR_PRIMAIRE_FONCEE = "#0c2c4f"
COULEUR_ACCENT = "#1a7a3c"
COULEUR_ACCENT_FOND = "#e5f4ea"
COULEUR_FOND_PAGE = "#eef1f5"
COULEUR_CARTE = "#ffffff"
COULEUR_TEXTE = "#1f2933"
COULEUR_TEXTE_MUTE = "#5a6472"
COULEUR_BORDURE = "#d3d9e0"

POLICE = "Helvetica"


def _formater_montant(valeur):
    """Formate un entier avec des espaces comme séparateurs de milliers."""
    return f"{valeur:,}".replace(",", " ")


class Application(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=0, style="Page.TFrame")
        self.master = master
        self.master.title("Simulateur de prime — Lanala Bank")
        self.master.configure(bg=COULEUR_FOND_PAGE)
        self.master.minsize(620, 680)
        self.master.resizable(True, True)
        self._centrer_fenetre(700, 780)

        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)

        self._configurer_style()
        self._construire_banniere()
        self._construire_formulaire()
        self._construire_zone_resultat()

    def _centrer_fenetre(self, largeur, hauteur):
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() - largeur) // 2
        y = max((self.master.winfo_screenheight() - hauteur) // 3, 0)
        self.master.geometry(f"{largeur}x{hauteur}+{x}+{y}")

    def _configurer_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Page.TFrame", background=COULEUR_FOND_PAGE)
        style.configure("Banniere.TFrame", background=COULEUR_PRIMAIRE)
        style.configure(
            "BanniereTitre.TLabel",
            background=COULEUR_PRIMAIRE,
            foreground="white",
            font=(POLICE, 19, "bold"),
        )
        style.configure(
            "BanniereSousTitre.TLabel",
            background=COULEUR_PRIMAIRE,
            foreground="#c7d7e8",
            font=(POLICE, 10),
        )

        style.configure(
            "Carte.TLabelframe",
            background=COULEUR_CARTE,
            bordercolor=COULEUR_BORDURE,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Carte.TLabelframe.Label",
            background=COULEUR_CARTE,
            foreground=COULEUR_PRIMAIRE,
            font=(POLICE, 12, "bold"),
        )

        style.configure("Carte.TFrame", background=COULEUR_CARTE)
        style.configure(
            "Champ.TLabel",
            background=COULEUR_CARTE,
            foreground=COULEUR_TEXTE,
            font=(POLICE, 11),
        )
        style.configure(
            "Mute.TLabel",
            background=COULEUR_CARTE,
            foreground=COULEUR_TEXTE_MUTE,
            font=(POLICE, 10, "italic"),
        )
        style.configure(
            "SousTitre.TLabel",
            background=COULEUR_CARTE,
            foreground=COULEUR_PRIMAIRE,
            font=(POLICE, 12, "bold"),
        )

        style.configure("TEntry", fieldbackground="white", padding=6)
        style.configure("TCombobox", fieldbackground="white", padding=6)

        style.configure(
            "Primaire.TButton",
            background=COULEUR_PRIMAIRE,
            foreground="white",
            font=(POLICE, 12, "bold"),
            padding=(18, 10),
            borderwidth=0,
        )
        style.map(
            "Primaire.TButton",
            background=[("active", COULEUR_PRIMAIRE_FONCEE), ("pressed", COULEUR_PRIMAIRE_FONCEE)],
        )

        style.configure(
            "Secondaire.TButton",
            background=COULEUR_FOND_PAGE,
            foreground=COULEUR_PRIMAIRE,
            font=(POLICE, 11),
            padding=(16, 10),
            borderwidth=1,
        )
        style.map("Secondaire.TButton", background=[("active", "#dfe6ee")])

        style.configure(
            "DetailLibelle.TLabel",
            background=COULEUR_CARTE,
            foreground=COULEUR_TEXTE,
            font=(POLICE, 11, "bold"),
        )
        style.configure(
            "DetailTaux.TLabel",
            background=COULEUR_CARTE,
            foreground=COULEUR_TEXTE_MUTE,
            font=(POLICE, 10),
        )
        style.configure(
            "DetailMontant.TLabel",
            background=COULEUR_CARTE,
            foreground=COULEUR_TEXTE,
            font=(POLICE, 11, "bold"),
        )

        style.configure("TotalBox.TFrame", background=COULEUR_ACCENT_FOND)
        style.configure(
            "TotalLibelle.TLabel",
            background=COULEUR_ACCENT_FOND,
            foreground=COULEUR_TEXTE,
            font=(POLICE, 13),
        )
        style.configure(
            "TotalValeur.TLabel",
            background=COULEUR_ACCENT_FOND,
            foreground=COULEUR_ACCENT,
            font=(POLICE, 26, "bold"),
        )

    def _construire_banniere(self):
        banniere = ttk.Frame(self, style="Banniere.TFrame")
        banniere.grid(row=0, column=0, sticky="ew")
        banniere.columnconfigure(0, weight=1)

        ttk.Label(
            banniere,
            text="Simulateur de prime d'assurance emprunteur",
            style="BanniereTitre.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(18, 2))
        ttk.Label(
            banniere,
            text="Lanala Bank — simulation 100% hors ligne",
            style="BanniereSousTitre.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))

    def _construire_formulaire(self):
        conteneur = ttk.Frame(self, style="Page.TFrame")
        conteneur.grid(row=1, column=0, sticky="ew", padx=24, pady=(20, 0))
        conteneur.columnconfigure(0, weight=1)

        formulaire = ttk.LabelFrame(
            conteneur, text="Informations de simulation", padding=20, style="Carte.TLabelframe"
        )
        formulaire.grid(row=0, column=0, sticky="ew")
        formulaire.columnconfigure(1, weight=1)

        ttk.Label(formulaire, text="Garantie *", style="Champ.TLabel").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.combo_garantie = ttk.Combobox(
            formulaire, state="readonly", values=list(LIBELLE_A_ID_GARANTIE.keys())
        )
        self.combo_garantie.grid(row=0, column=1, sticky="ew", pady=8, padx=(14, 0))

        ttk.Label(
            formulaire, text="Date de naissance (JJ/MM/AAAA) *", style="Champ.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=8)
        self.entree_date = ttk.Entry(formulaire)
        self.entree_date.grid(row=1, column=1, sticky="ew", pady=8, padx=(14, 0))

        ttk.Label(formulaire, text="Montant du prêt *", style="Champ.TLabel").grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.var_montant = tk.StringVar()
        self.var_montant.trace_add("write", self._on_montant_saisi)
        self.entree_montant = ttk.Entry(formulaire, textvariable=self.var_montant)
        self.entree_montant.grid(row=2, column=1, sticky="ew", pady=8, padx=(14, 0))

        ttk.Label(
            formulaire, text="Durée de remboursement (mois) *", style="Champ.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=8)
        self.entree_duree = ttk.Entry(formulaire)
        self.entree_duree.grid(row=3, column=1, sticky="ew", pady=8, padx=(14, 0))

        ttk.Label(
            formulaire, text="* champ obligatoire", style="Mute.TLabel"
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        boutons = ttk.Frame(conteneur, style="Page.TFrame")
        boutons.grid(row=1, column=0, sticky="w", pady=18)
        ttk.Button(
            boutons, text="Simuler", style="Primaire.TButton", command=self._on_simuler
        ).pack(side="left")
        ttk.Button(
            boutons, text="Réinitialiser", style="Secondaire.TButton", command=self._on_reinitialiser
        ).pack(side="left", padx=(12, 0))

        self._conteneur_principal = conteneur

    def _construire_zone_resultat(self):
        self.cadre_resultat = ttk.LabelFrame(
            self._conteneur_principal,
            text="Résultat de la simulation",
            padding=20,
            style="Carte.TLabelframe",
        )
        self.cadre_resultat.grid(row=2, column=0, sticky="ew", pady=(0, 24))
        self.cadre_resultat.columnconfigure(0, weight=1)
        self.cadre_resultat.grid_remove()  # caché tant qu'aucune simulation n'a réussi

        self.label_age = ttk.Label(self.cadre_resultat, text="", style="Champ.TLabel")
        self.label_age.grid(row=0, column=0, sticky="w")

        self.label_duree = ttk.Label(self.cadre_resultat, text="", style="Champ.TLabel")
        self.label_duree.grid(row=1, column=0, sticky="w", pady=(2, 0))

        ttk.Label(self.cadre_resultat, text="Détail par garantie", style="SousTitre.TLabel").grid(
            row=2, column=0, sticky="w", pady=(16, 8)
        )

        self.cadre_details = ttk.Frame(self.cadre_resultat, style="Carte.TFrame")
        self.cadre_details.grid(row=3, column=0, sticky="ew")
        self.cadre_details.columnconfigure(2, weight=1)

        ttk.Separator(self.cadre_resultat).grid(row=4, column=0, sticky="ew", pady=16)

        boite_total = ttk.Frame(self.cadre_resultat, style="TotalBox.TFrame")
        boite_total.grid(row=5, column=0, sticky="ew")
        boite_total.columnconfigure(1, weight=1)
        ttk.Label(boite_total, text="Prime totale", style="TotalLibelle.TLabel").grid(
            row=0, column=0, sticky="w", padx=16, pady=14
        )
        self.label_total = ttk.Label(boite_total, text="", style="TotalValeur.TLabel")
        self.label_total.grid(row=0, column=1, sticky="e", padx=16, pady=14)

    def _on_montant_saisi(self, *_args):
        texte = self.var_montant.get()
        position_curseur = self.entree_montant.index(tk.INSERT)
        chiffres_avant_curseur = sum(1 for c in texte[:position_curseur] if c.isdigit())

        chiffres = "".join(c for c in texte if c.isdigit())
        formate = _formater_montant(int(chiffres)) if chiffres else ""

        if formate == texte:
            return

        self.var_montant.set(formate)

        nouvelle_position = len(formate)
        vus = 0
        for i, c in enumerate(formate):
            if vus == chiffres_avant_curseur:
                nouvelle_position = i
                break
            if c.isdigit():
                vus += 1
        self.entree_montant.icursor(nouvelle_position)

    def _lire_date_naissance(self):
        texte = self.entree_date.get().strip()
        if not texte:
            return None
        try:
            return datetime.strptime(texte, "%d/%m/%Y").date()
        except ValueError:
            raise ErreurValidation("Format de date invalide. Utilisez JJ/MM/AAAA.")

    def _lire_entier(self, texte, message_si_invalide):
        texte = texte.strip().replace(" ", "")
        if not texte:
            return None
        try:
            return int(texte)
        except ValueError:
            raise ErreurValidation(message_si_invalide)

    def _on_simuler(self):
        try:
            garantie = LIBELLE_A_ID_GARANTIE.get(self.combo_garantie.get())
            if garantie is None:
                raise ErreurValidation(MESSAGES["garantie_manquante"])

            date_naissance = self._lire_date_naissance()
            montant = self._lire_entier(self.entree_montant.get(), MESSAGES["montant_invalide"])
            duree = self._lire_entier(self.entree_duree.get(), MESSAGES["duree_hors_plage"])

            resultat = simuler(garantie, date_naissance, montant, duree)
        except ErreurValidation as erreur:
            self.cadre_resultat.grid_remove()
            messagebox.showerror("Erreur de saisie", str(erreur))
            return

        self._afficher_resultat(resultat)

    def _afficher_resultat(self, resultat):
        self.label_age.config(text=f"Âge calculé : {resultat['age']} ans")

        if resultat["duree_saisie"] != resultat["palier"]:
            self.label_duree.config(
                text=(
                    f"Durée saisie : {resultat['duree_saisie']} mois "
                    f"— tarifée sur {resultat['palier']} mois"
                )
            )
        else:
            self.label_duree.config(text=f"Durée : {resultat['palier']} mois")

        for widget in self.cadre_details.winfo_children():
            widget.destroy()
        for i, detail in enumerate(resultat["details"]):
            ttk.Label(self.cadre_details, text=detail["libelle"], style="DetailLibelle.TLabel").grid(
                row=i, column=0, sticky="w", pady=5
            )
            ttk.Label(
                self.cadre_details, text=f"taux {detail['taux']:.2f} %", style="DetailTaux.TLabel"
            ).grid(row=i, column=1, sticky="w", padx=(16, 0), pady=5)
            ttk.Label(
                self.cadre_details,
                text=_formater_montant(detail["montant"]),
                style="DetailMontant.TLabel",
            ).grid(row=i, column=2, sticky="e", pady=5)

        self.label_total.config(text=_formater_montant(resultat["total"]))

        self.cadre_resultat.grid()

    def _on_reinitialiser(self):
        self.combo_garantie.set("")
        self.entree_date.delete(0, tk.END)
        self.var_montant.set("")
        self.entree_duree.delete(0, tk.END)
        self.cadre_resultat.grid_remove()


def lancer_application():
    racine = tk.Tk()
    Application(racine)
    racine.mainloop()
