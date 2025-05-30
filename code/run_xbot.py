'''
Authors: Sen Chen and Lingling Fan
'''

import subprocess
import csv
import os

from lxml.isoschematron import stylesheet_params

import repkg_apk
import explore_activity
import shutil
import sys


emulator = 'emulator-5554'

apkPath = 'E:/pythonProject/Xbot-main/main-folder/apks'


java_home_path = 'C:\Program Files\Java\jdk-17'

sdk_platform_path = 'E:/pythonProject/Xbot-main/main-folder/config/libs/android-platforms/' # For Ubuntu (TJU-Computer)

lib_home_path = 'E:/pythonProject/Xbot-main/main-folder/config/libs/' # For Ubuntu (TJU-Computer)


accessbility_folder = os.path.dirname(os.path.dirname(apkPath)) # Main folder of project

config_folder = os.path.join(accessbility_folder, "config")

results_folder = os.path.join(accessbility_folder, "results")

storydroid_folder = os.path.join(accessbility_folder, "storydroid")

decompilePath = os.path.join(results_folder, "apktool")  # decompiled app path (apktool handled)

repackagedAppPath = os.path.join(results_folder, "repackaged")  # store the repackaged apps

keyPath = os.path.join(config_folder, "coolapk.keystore") # pwd: 123456, private key path

results_outputs = os.path.join(results_folder, "outputs") # project results

tmp_file = os.path.join(results_folder, emulator).replace(os.sep, '/') # tmp file for parallel execution

def createOutputFolder():
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
        # print(results_folder)
    if not os.path.exists(storydroid_folder):
        os.makedirs(storydroid_folder)
        # print(storydroid_folder)
    if not os.path.exists(decompilePath):
        os.makedirs(decompilePath)

    if not os.path.exists(repackagedAppPath):
        os.makedirs(repackagedAppPath)

    if not os.path.exists(results_outputs):
        os.makedirs(results_outputs)

def execute(apk_path, apk_name,act_name):


    if not os.path.exists(os.path.join(repackagedAppPath, apk_name + '.apk')):


        r = repkg_apk.startRepkg(apk_path, apk_name, results_folder, config_folder)


        if r == 'no manifest file' or r == 'build error' or  r == 'sign error':
            print ('apk not successfully recompiled! will use the original app to execute')

    new_apkpath = os.path.join(repackagedAppPath, apk_name + '.apk')


    if os.path.exists(new_apkpath):

        explore_activity.exploreActivity(new_apkpath, apk_name, results_folder, emulator, tmp_file, paras_path,act_name)

def run_soot(apk_path, pkg): #Get bundle data for UI page rendering

    soot_file = 'run_soot.run' # Binary file name
    os.chdir(config_folder)

    '''
    If uses jar
    '''
    #os.system('java -jar %s %s %s %s %s %s %s' % (soot_jar, storydroid_folder, apk_path, pkg, java_home_path, sdk_platform_path, lib_home_path))

    '''
    If uses binary
    '''
    print ('./%s %s %s %s %s %s %s' % (soot_file, storydroid_folder, apk_path, pkg,
                                                  java_home_path, sdk_platform_path, lib_home_path))
    os.system('./%s %s %s %s %s %s %s' % (soot_file, storydroid_folder, apk_path, pkg,
                                                  java_home_path, sdk_platform_path, lib_home_path))


def get_pkg(apk_path): # This version has a problem about pkg, may inconsist to the real pkg
    cmd = "aapt dump badging %s | grep 'package' | awk -v FS=\"'\" '/package: name=/{print$2}'" % apk_path
    defined_pkg_name = subprocess.getoutput(cmd)

    launcher = subprocess.getoutput(r"aapt dump badging " + apk_path + " | grep launchable-activity | awk '{print $2}'")
    if launcher.startswith(".") or defined_pkg_name in launcher or launcher == '' or launcher == '':
        return defined_pkg_name
    else:
        used_pkg_name = launcher.replace('.' + launcher.split('.')[-1], '').split('\'')[1]
        return used_pkg_name

def remove_folder(apkname, decompilePath):
    folder = os.path.join(decompilePath, apkname)
    if not os.path.exists(folder):
        return
    
    for f in os.listdir(folder):
        if not f == 'AndroidManifest.xml':
            rm_path = os.path.join(folder, f)
            if os.path.exists(rm_path):
                try:
                    if os.path.isdir(rm_path):
                        os.chmod(rm_path,0o777)
                        shutil.rmtree(rm_path)
                    else:
                        os.remove(rm_path)
                except PermissionError as e:
                    print(f"Permission error when deleting {rm_path}: {e}")
                except FileNotFoundError as e:
                    print(f"File not found {rm_path}: {e}")
                except Exception as e:
                    print(f"Error removing {rm_path}: {e}")
            else:
                print(f"Path does not exist: {rm_path}")

def run_all(act_name):
    createOutputFolder()  # Create the folders if not exists

    out_csv = os.path.join(results_folder, 'log.csv')
    if not os.path.exists(out_csv):
        csv.writer(open(out_csv, 'a')).writerow(('apk_name', 'pkg_name', 'all_act_num', 'launched_act_num',
                                                 'act_not_launched','act_num_with_issue'))

    for apk in os.listdir(apkPath): # Run the apk one by one

        if not 'apks' in apk and 'apk' in apk:

            root = 'adb -s %s root' % (emulator) # root the emulator before running
            print (subprocess.getoutput(root))

            apk_path = os.path.join(apkPath, apk) # Get apk path

            apk_name = apk.rstrip('.apk') # Get apk name
            pkg = get_pkg(apk_path) # Get pkg, this version has a problem about pkg, may inconsist to the real pkg

            print ('======= Starting ' + apk_name + ' =========')

            '''
            Get Bundle Data
            Trade off by users, open or close
            '''
            #run_soot(apk_path, pkg) # get intent parameters

            global paras_path
            paras_path = os.path.join(storydroid_folder,'outputs',apk_name,'activity_paras.txt')
            # paras_path = storydroid_folder + '/outputs/' + apk_name + '/activity_paras.txt'

            if not os.path.exists(storydroid_folder + '/outputs/' + apk_name):
                output_path = os.path.join(storydroid_folder, 'outputs', apk_name)
                os.makedirs(output_path, exist_ok=True)
                # os.mkdir(storydroid_folder + '/outputs/' + apk_name)
            if not os.path.exists(paras_path):
                ## os.mknod(paras_path) # It is not avaiable for macbook
                open(paras_path, 'w').close()

            '''
            Core
            '''
            # print('--------------------------------------')
            execute(apk_path, apk_name,act_name)
            # print('--------------------------------------')
            if os.path.exists(apk_path):
                os.remove(apk_path) # Delete the apk

            if os.path.exists(os.path.join(repackagedAppPath, apk_name + '.apk')):
                os.remove(os.path.join(repackagedAppPath, apk_name + '.apk'))

            # print("*************************************")

            # Remove the decompiled and modified resources
            remove_folder(apk_name, decompilePath)

