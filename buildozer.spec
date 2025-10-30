[app]

# Titre de l'application
title = LeTousgestions

# Nom du package
package.name = letousgestions

# Domaine
package.domain = org.letousgestions

# Chemin vers le code source
source.dir = .

# Fichier principal
source.include_exts = py,png,jpg,kv,atlas,ttf

# Version de l'application
version = 1.0.0

# Requirements (simplifiés pour éviter les conflits)
requirements = python3,kivy

# Configuration Android
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34

# Configuration p4a
p4a.bootstrap = sdl2

# Permissions Android
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Architecture Android (une seule pour simplifier)
android.arch = arm64-v8a

# Orientation
orientation = portrait

# Comportement de la fenêtre
fullscreen = 0
window.resizeable = 0

# Log level
log_level = 2

# Règles de compilation
android.allow_backup = true

[buildozer]
log_level = 2
build_dir = ./.buildozer
bin_dir = ./bin
