[app]
title = Simulateur de prime Lanala
package.name = simulateurprimelanala
package.domain = com.lanalabank

source.dir = .
source.include_exts = py

version = 1.0.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Aucune permission réseau : l'application est 100% hors ligne
# (cahier des charges — aucune donnée ne doit sortir de l'appareil).
android.permissions =

android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
