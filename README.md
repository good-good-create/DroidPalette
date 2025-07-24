# DroidPalette

# Annotation of emprical study.xlsx
1.1 in column B indicates that it belongs to T1.1.<br>
1.2 in column B indicates that it belongs to T1.2.<br>
1.1 + 1.2 in column B indicates that it belongs to T1.1 + T1.2.<br>
1? in column B indicates that it not belongs to T1.1 or T1.2.<br>

2 in column B indicates that it belongs to T2.<br>
3 in column B indicates that it belongs to T3.<br>


1 in column C indicates that it belongs to "generating patches by modifying XML configuration files".<br>
2 in column C indicates that it belongs to "generating patches by modifying the Android code framework, such as Java code".<br>
3 in column C indicates that it belongs to "generating patches by combining the above two approaches, but the modification to the Android framework code in this case can be achieved through changes to the XML configuration files".<br>

Column J indicates the number of stars for the project corresponding to the current empirical study.
Column K indicates the number of code lines in the project corresponding to the current empirical study.


# The URL address of the survey.
https://forms.gle/GGtPYgYPSfoREYBv5

# Environment Configuration
- Windows
- Python:3.8
- ApkTool:2.10.0

# Usage

In main.py, please provide the following parameters:
- decomp_path: The directory path where the decompiled APK files will be output.
- report_path: The path to Xbot's detection results.
- apk_path: The path to the problematic APK file.
- original_issue_path: The backup path for the original detection results from Xbot.

Usage:python main.py
  
