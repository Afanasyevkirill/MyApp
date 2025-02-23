[buildozer]
title = My App
package.name = myapp
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
requirements = kivy, requests
version = 1.0
version.name = 1.0
presplash.filename = data/presplash.png
icon.filename = data/icon.png

[android]
android.api = 19
android.minapi = 19
android.sdk = 29
android.ndk = 21b
android.permissions = INTERNET
android.arch = armeabi-v7a, arm64-v8a
fullscreen = 1
orientation = portrait

[p4a]
p4a.branch = stable
p4a.version = stable
