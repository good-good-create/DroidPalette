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
- 打开Android Studio，在Device Manager选择Create Visual Device。
- Visual Device选择Pixel，屏幕分辨率选择1080×1920，API选择33+。
- 打开新创建的虚拟机，你需要安装Google Accessibility Scanner工具。
- 执行上述步骤之后，在run_xbot.py文件内将emulator信息填写完整。

Run


# Usage

In main.py, please provide the following parameters:
- decomp_path: The directory path where the decompiled APK files will be output.
- report_path: The path to Xbot's detection results.
- apk_path: The path to the problematic APK file.
- original_issue_path: The backup path for the original detection results from Xbot.

Usage : python main.py
  
