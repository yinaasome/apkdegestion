[app]
title = LeTousgestions
package.name = letousgestions
package.domain = org.letousgestions

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0
requirements = python3,kivy,firebase_admin,requests,urllib3,chardet,idna,certifi,pytz

presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0

[buildozer]
log_level = 2

[app]
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.gradle_download = https://services.gradle.org/distributions/gradle-7.6-all.zip

android.accept_sdk_license = True

[buildozer]
log_level = 2

[app]
android.arch = arm64-v8a

# Configuration pour les builds plus rapides
android.skip_build_app = False
android.private_storage = True
