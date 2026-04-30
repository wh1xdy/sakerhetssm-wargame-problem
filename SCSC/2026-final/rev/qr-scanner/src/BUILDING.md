Get the Android SDK and NDK.  
Get Qt6 for Android with Multimedia.

Configure CMake through the following command (remember to replace placeholder values and change to appropriate paths)
```sh
$ ~/Qt/{QT_VERSION}/android_arm64_v8a/bin/qt-cmake -B build-android -GNinja -DCMAKE_BUILD_TYPE=Release -DANDROID_SDK_ROOT="$HOME/Android/Sdk" -DANDROID_NDK_ROOT="$HOME/Android/Sdk/ndk/{NDK_VERSION}" -DCMAKE_SYSTEM_NAME="Android" -DCMAKE_ANDROID_ARCH_ABI=arm64-v8a -DQT_ANDROID_SIGN_APK=ON
```

Build the APK with a debug keystore:
```sh
QT_ANDROID_KEYSTORE_PATH=$HOME/.android/debug.keystore QT_ANDROID_KEYSTORE_ALIAS=androiddebugkey QT_ANDROID_KEYSTORE_STORE_PASS=android QT_ANDROID_KEYSTORE_KEY_PASS=android cmake --build build-android --target apk
```
