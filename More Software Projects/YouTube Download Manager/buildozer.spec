[app]

source.dir = .
version = 1.0.0


# (other app settings above)

package.name = myapp
package.domain = org.test
package.relocated = False

android.permissions = INTERNET

# Disable SSL certificate verification
android.meta_data = android.app.disable_ssl_certificate_validation: 'true'

# (str) Title of your application
title = My Application

# (str) Source code where the main.py live
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = python3,kivy
requirements = python3,kivy

# (list) Supported orientations
orientation = portrait

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 20

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a
