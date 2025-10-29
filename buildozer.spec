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
requirements = python3,kivy,firebase_admin,pyjnius,openssl,requests,urllib3

# Version de Python
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# Configuration Android
osx.android.api = 33
osx.android.minapi = 21
osx.android.ndk = 25b
osx.android.sdk = 34
osx.android.gradle_download = True

# Permissions Android
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Features Android
android.features = android.hardware.touchscreen

# Architecture Android
android.arch = arm64-v8a,armeabi-v7a

# Configuration de build
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

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

# Services (optionnel pour certaines fonctionnalités)
# services = Letousgestions:service

# Configuration iOS (si nécessaire)
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master
# ios.arch = arm64

# Configuration de release
# (Décommentez pour les builds de release)
# android.release_artifact = .apk
# android.aab = 0

# Numéro de version (augmentez à chaque release)
# android.numeric_version = 1

# Configuration Windows (optionnel)
# osx.windows.sdk_version = 
# osx.windows.visualstudio_version = 
# osx.windows.target_platform = 

# Configuration macOS (optionnel)
# osx.osx.python_version = 3
# osx.osx.sdk_version = 
# osx.osx.deploy_target = 

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
