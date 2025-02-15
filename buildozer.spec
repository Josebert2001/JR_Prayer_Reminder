[app]

# (str) Title of your application
title = JR Prayer Reminder

# (str) Package name
package.name = jrprayerreminder

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py is located
source.include_exts = py,png,jpg,kv,atlas

# (list) Permissions
android.permissions = INTERNET

# (list) Requirements
requirements = python3,kivy,kivymd,requests

# (str) Main script
source.main = main.py

# (str) Supported orientation (one of: landscape, landscape-reverse, portrait or portrait-reverse)
orientation = portrait

# (str) Application versioning
version = 0.1

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) Icon of the application
icon.filename = icon.png

# (list) Supported platforms
# android will be included by default
# available platforms: android, ios, win, linux, macosx, web
supported_platforms = android