import os
import subprocess


import os
import subprocess

def sign_apk(apk_name, decompileAPKPath, repackagedAppPath):

    repackName = apk_name + ".apk"
    resign_appName = apk_name + "_sign" + ".apk"
    repackAppPath = os.path.join(decompileAPKPath, 'dist', repackName)
    sign_apk_path = os.path.join(repackagedAppPath, resign_appName)
    keyPath = 'C:/Users/Administrator/Desktop/yjs/x-bot/Xbot-main/main-folder/config/coolapk.keystore'
    keyAlias = "coolapk"
    keystorePassword = "123456"
    keyPassword = "123456"

    print(f"Key path: {keyPath}")
    print(f"Unsigned APK path: {repackAppPath}")
    print(f"Signed APK path: {sign_apk_path}")


    if not os.path.exists(repackAppPath):
        print(f"Error: Input APK not found at {repackAppPath}")
        return "fail"


    os.makedirs(repackagedAppPath, exist_ok=True)


    cmd = [
        "apksigner", "sign",
        "--ks", keyPath,
        "--ks-key-alias", keyAlias,
        "--ks-pass", f"pass:{keystorePassword}",
        "--key-pass", f"pass:{keyPassword}",
        "--out", sign_apk_path,
        repackAppPath
    ]

    try:

        result = subprocess.run(cmd, text=True, capture_output=True, check=True)


        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")

        if result.returncode == 0:
            print("Sign success...................................................")
            return "success"
        else:
            print(f"Apksigner failed with error code {result.returncode}")
            return "fail"

    except subprocess.CalledProcessError as e:
        print(f"Error during signing process: {e.stderr}")
        return "fail"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "fail"


# example
input_apk_path = 'C:/Users/Administrator/Desktop/temp/org.secuso.privacyfriendlynotes_20.apk'
apk_name = 'org.secuso.privacyfriendlynotes_20'
output_apk_path = 'C:/Users/Administrator/Desktop/temp_sign/org.secuso.privacyfriendlynotes_20.apk'

sign_apk(apk_name,input_apk_path,output_apk_path)