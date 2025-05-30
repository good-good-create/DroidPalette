# encoding: utf-8

from pathlib import Path
import os
import shutil
#import commands
import subprocess
import time
import find_colors_set
import get_clickableID2
import find_problem_set
import modify_component
import run_xbot
from modify_component import modify_component_2
from run_xbot import run_all
import process_nothing_issue
from multiprocessing import Process
from pathlib import Path

results_folder = "E:/pythonProject/repaired"


issue_apk_path = 'E:/pythonProject/issue_apk'

apktool_path = 'D:/Apktool'

f_num = 0


def del_file(directory,act_name):
    dst_path = os.path.join(directory,act_name)

    try:
        shutil.rmtree(dst_path)
    except FileNotFoundError:
        print(f"{dst_path} not exist")
    except PermissionError:
        print(f"no permission : {dst_path}")
    except Exception as e:
        print(f"error: {e}")

def decompile(eachappPath, decompileAPKPath):
    print ("decompiling...")
    cmd = "apktool d {0} -f -o {1}".format(eachappPath, decompileAPKPath)
    os.system(cmd)

def recompile(decompileAPKPath, repackagedAppPath, recompileAPKName):
    print ("recompile...")
    cmd = "apktool b {0} -o {1}".format(decompileAPKPath, os.path.join(repackagedAppPath, recompileAPKName))
    result = subprocess.run([cmd],stdout=subprocess.PIPE,text=True)
    output = result.stdout
    return output


def repair_process(act_name,decomp_path,report_path,app_name):
    global f_num
    pre_component_issue = {}
    cur_component_issue = {}
    component_with_issue = {}
    no_id_text_issue = []
    text_seq = 0
    image_seq = 0

    # app_name = 'org.rocstreaming.rocdroid_2001'
    report_path = os.path.join(report_path,app_name)
    # print(act_name)

    component_with_issue = find_problem_set.find_issue(act_name,report_path)

    # print(f"123:{component_with_issue}")


    component_with_issue = find_problem_set.trans_text_to_string(component_with_issue,decomp_path)
    # print(component_with_issue)

    colors_set = find_colors_set.find_colors(act_name,report_path)

    component_with_issue = find_colors_set.find_replace_color(component_with_issue,colors_set)
    component_with_issue = find_colors_set.process_same_dict(component_with_issue)

    pre_component_issue = component_with_issue


    report_first_path = 'E:/pythonProject/Xbot-main/results/outputs'
    # del_file(report_first_path)

    no_id_text_issue = find_problem_set.find_nothing_issue(act_name,report_path)


    while pre_component_issue:


        text_seq,image_seq = modify_component.modify_component(decomp_path, pre_component_issue, text_seq, image_seq)

        if (text_seq >= 3 or image_seq >= 3) and f_num == 0:
            if image_seq >= 3:
                modify_component.last_change_image(decomp_path,pre_component_issue)
            f_num = 1

        recompileInfo = modify_component.recompile_apk(decomp_path)


        recomp_apk_path = os.path.join(decomp_path,'dist')

        for filename in os.listdir(recomp_apk_path):
            print(f'dist filename : {filename}')

        target_dir = 'E:/pythonProject/Xbot-main/main-folder/apks'
        modify_component.move_apk_to_target(recomp_apk_path,target_dir)


        report_first_path = os.path.join(report_first_path,app_name,'issues')
        del_file(report_first_path,act_name)
        run_all(act_name)

        if text_seq >= 3 or image_seq >= 3:
            break


        cur_component_issue = find_problem_set.find_issue(act_name,report_path)


        cur_component_issue = find_problem_set.trans_text_to_string(cur_component_issue,decomp_path)

        cur_component_issue = find_colors_set.find_replace_color(cur_component_issue,colors_set)
        cur_component_issue = find_colors_set.process_same_dict(cur_component_issue)

        key_to_delete = []
        for key,(issue_color,issue_class,candidate_color,flag) in cur_component_issue.items():

            if key in pre_component_issue:


                modify_component_2(decomp_path,cur_component_issue,key,text_seq - 1,image_seq - 1,pre_component_issue[key][3])

                cur_component_issue[key] = (issue_color,issue_class,candidate_color,0)
            else:
                key_to_delete.append(key)

        for key in key_to_delete:
            del cur_component_issue[key]
        pre_component_issue = cur_component_issue

        if pre_component_issue == {}:
            break

        if pre_component_issue!= {} and (text_seq >= 3 or image_seq >= 3):
            pre_component_issue = modify_component.modify_child(decomp_path,pre_component_issue)
            image_seq = 0
            text_seq = 0

def repair_apk(report_path,apk_path,apk_all_name,decomp_path,orginal_issue_path):
        global f_num


        issue_path = os.path.join(orginal_issue_path,"issues")
        issue_path = Path(issue_path)

        for act in issue_path.iterdir():
            if act.is_dir():
                act_name = act.name
                repair_process(act_name,decomp_path,report_path,apk_all_name)
                if f_num == 1:
                    f_num = 0
        print("repair all success!")



apk_all_name = 'com.example.trigger_400'

decomp_path = f"D:/Apktool/{apk_all_name}" #The directory for decompiled APK files


report_path = 'E:/pythonProject/Xbot-main/results/outputs' #file path to issue report

apk_path = f'E:/pythonProject/issue_apk/{apk_all_name}' # issue apk path

orginal_issue_path = f'E:/orignal/{apk_all_name}' # Backup bug report address

repair_apk(report_path,apk_path,apk_all_name,decomp_path,orginal_issue_path)



