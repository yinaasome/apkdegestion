[app]

# Titre de l'application
title = LeTousgestions

# Nom du package
package.name = letousgestions

# Domaine (inverse de votre nom de domaine)
package.domain = org.letousgestions

# Chemin vers le code source
source.dir = .

# Fichier principal
source.include_exts = py,png,jpg,kv,atlas,ttf

# Version de l'application
version = 1.0.0

# Requirements
requirements = python3,kivy,openssl,requests,urllib3,pyjnius

# Version de Python
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# Configuration Android
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.gradle_download = True

# Permissions Android
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Features Android
android.features = android.hardware.touchscreen

# Architecture Android
android.arch = arm64-v8a,armeabi-v7a

# Configuration de build
#presplash.filename = %(source.dir)s/assets/presplash.png
#icon.filename = %(source.dir)s/assets/icon.png

# Orientation
orientation = portrait

# Comportement de la fenêtre
fullscreen = 0
window.resizeable = 0

# Log level
log_level = 2

# Bootstrap
android.bootstrap = sdl2

# Entrée utilisateur
android.entrypoint = org.kivy.android.PythonActivity

# Règles d'inclusion/exclusion
android.add_src = 
android.add_resources = 

# Règles de compilation
android.allow_backup = true
android.accept_sdk_license = false

# Numéro de version (augmentez à chaque release)
# android.numeric_version = 1

[buildozer]

# Configuration de Buildozer
log_level = 2
warn_on_root = 1
warn_on_failure = 1

# Répertoire de build
build_dir = ./.buildozer

# Cache pour les dépendances
bin_dir = ./.bin

# Dossier de sortie des APK
bin_dir = ./bin
