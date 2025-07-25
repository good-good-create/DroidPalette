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
Run the following command in the directory where the code/main.py file is located to execute DroidPalette:
<pre>python main.py</pre>

# Usage

In main.py, please provide the following parameters:
- decomp_path: The directory path where the decompiled APK files will be output.
- report_path: The path to Xbot's detection results.
- apk_path: The path to the problematic APK file.
- original_issue_path: The backup path for the original detection results from Xbot.

Usage : python main.py
  
