# DroidPalette

# The URL address of the survey.
https://forms.gle/GGtPYgYPSfoREYBv5

# The URL address of DroidPalette's experimental dataset
https://drive.google.com/file/d/136trbD78Z0P0r4b5OZp1xzgCbz-ZdGKp/view?usp=drive\_link

# Environment Configuration
- Windows10
- Python:3.8
- ApkTool:2.10.0
- Android SDK:API 35+

# Getting Started

Setting up
- Open Android Studio and select "Create Virtual Device" in the Device Manager.
- For the Virtual Device, select Pixel, set the screen resolution to 1080×1920, and choose API level 33 or higher.
- Open the newly created virtual device, and you need to install the Google Accessibility Scanner tool.
- After completing the above steps, fill in the emulator information in the `run_xbot.py`.

Run</br>
- Run the following command in the directory where the `main.py` is located to execute DroidPalette:
<pre>python main.py</pre>

# Detailed Description

Input: the APK file of the problematic app to be repaired and its detection results (detected by Xbot)</br>
Output: a new APK file repaired by DroidPalette</br>

All Optional Parameters of DroidPalette
- `report_path`: The path to Xbot's detection results.
- `apk_path`: The path to the problematic APK file.
- `apk_all_name`: The name of the APK file to be repaired.
- `decomp_path`: The output directory path of the decompiled APK file.
- `orginal_issue_path`: The location of the backup file for the original detection report of the problematic APK to be repaired.
- `repair_path`: The location of the repaired APK file.
- `apktool_path`: The location of apktool

The set of candidate attributes is provided by ConfDroid, and the specific implementation details can be referred to at: https://sites.google.com/view/confdroid </br>


