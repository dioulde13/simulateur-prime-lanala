"""Configuration py2app pour générer une application Mac native (.app)
à partir du simulateur. Utilisation :

    python3.12 -m pip install py2app
    python3.12 setup.py py2app

L'app générée se trouve ensuite dans dist/SimulateurPrimeLanala.app —
double-cliquable, sans besoin d'installer Python sur la machine cible.
"""

from setuptools import setup

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "SimulateurPrimeLanala",
        "CFBundleDisplayName": "Simulateur de prime - Lanala Bank",
        "CFBundleIdentifier": "com.lanalabank.simulateurprime",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright": "Lanala Bank",
        "LSUIElement": False,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
