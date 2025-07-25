# DroidPalette

# The URL address of the survey.
https://forms.gle/GGtPYgYPSfoREYBv5

# Environment Configuration
- Windows
- Python:3.8
- ApkTool:2.10.0
- Android SDK:API 35+

# Getting Started

Setting up
- Open Android Studio and select "Create Virtual Device" in the Device Manager.
- For the Virtual Device, select Pixel, set the screen resolution to 1080×1920, and choose API level 33 or higher.
- Open the newly created virtual device, and you need to install the Google Accessibility Scanner tool.
- After completing the above steps, fill in the emulator information in the `run_xbot.py` file.

Run</br>
- Run the following command in the directory where the code/main.py file is located to execute DroidPalette:
<pre>python main.py</pre>

# Detailed Description
All Optional Parameters of SetDroid
- `report_path`: The path to Xbot's detection results.
- `apk_path`: The path to the problematic APK file.
- `apk_all_name`: The name of the APK file to be repaired.
- `decomp_path`: The output directory path of the decompiled APK file.
- `orginal_issue_path`: The location of the backup file for the original detection report of the problematic APK to be repaired.
- `repair_path`: The location of the repaired APK file.

Input: the APK resource file of the problematic app to be repaired and its detection results (detected by Xbot)
Output: a new APK file repaired by DroidPalette

