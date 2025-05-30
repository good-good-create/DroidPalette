'''
Authors: Sen Chen and Lingling Fan
'''

import os, subprocess, shutil
import time, csv
import re
import xml.etree.ElementTree as ET
import zipfile
from importlib.metadata import files

from jedi.inference import follow_error_node_imports_if_possible
from jupyter_server.services.contents.fileio import path_to_invalid
from numpy.lib.utils import source

#adb = '/home/senchen/genymotion_3.0.0/genymotion/tools/adb'
#adb = "adb -s %s"%(run_rpk_explore_apk.emulator)
#folder_name = run.folder_name
#tmp_dir = run_rpk_explore_apk.tmp_file

adb = ''
tmp_dir = ''
act_paras_file = ''
defined_pkg_name = ''
used_pkg_name = ''

def zipalign_apk(input_apk_path):
    input_apk = os.path.abspath(input_apk_path)
    file_name,file_extension = os.path.splitext(input_apk)
    output_apk = file_name + '_aligned.apk'


    cmd = f'zipalign -p -f -v 4 {input_apk} {output_apk}'
    subprocess.run(cmd,shell = True,check = True)

    os.remove(input_apk)

    os.rename(output_apk,input_apk)

    return 'Success'

def installAPP(new_apkpath, apk_name, results_folder):

    appPath = new_apkpath
    get_pkgname(appPath)
    adb = 'adb.exe'

    cmd = adb + " install -r " + appPath
    out = subprocess.getoutput(cmd)
    for o in out.split('\n'):
        if 'Failure' in o or 'Error' in o:
            print ('install failure: %s'%apk_name)
            print (out)
            csv.writer(open(os.path.join(results_folder, 'installError.csv'),'a')).writerow((apk_name, out.replace('\n', ', ')))
            return 'Failure'
    print ('Install Success')

    return 'Success'

def uninstallApp(package):
    cmd = adb + " uninstall " + package
    os.system(cmd)

def scan_and_return():

    time.sleep(1)
    adb = 'adb.exe'

    os.system(f'{adb} shell input tap 548 530')
    time.sleep(5)

    os.system(f'{adb} shell input tap 920 140')
    time.sleep(4)


    os.system(f'{adb} shell input keyevent HOME')
    time.sleep(4)

def clean_tmp_folder(folder):

    if not os.path.exists(folder):
        return

    for f in os.listdir(folder):
        file_path = os.path.join(folder,f)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)



def unzip(zip_file, activity):



    issue_folder = zip_file.split('.zip')[0]

    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(issue_folder)
            print(f"Unzipped {zip_file} to {issue_folder}")
    except Exception as e:
        print(f"Error unzipping file: {e}")
        return

    if os.path.exists(zip_file):
        os.remove(zip_file)
        print(f"Deleted zip file: {zip_file}")


    if os.path.exists(issue_folder) and os.path.isdir(issue_folder):
        for f in os.listdir(issue_folder):
            file_path = os.path.join(issue_folder, f)

            if f.endswith('.png'):
                new_name = f"{activity}.png"
                new_path = os.path.join(issue_folder, new_name)

                if os.path.exists(new_path):
                    os.remove(new_path)

                os.rename(file_path, new_path)
                print(f"Renamed {f} to {new_name}")

            if f.endswith('.txt'):
                new_name = f"{activity}.txt"
                new_path = os.path.join(issue_folder, new_name)

                if os.path.exists(new_path):
                    os.remove(new_path)

                os.rename(file_path, new_path)
                print(f"Renamed {f} to {new_name}")


def adb_pull_zip_from_device(remote_dir, local_dir):
    try:

        adb = 'adb.exe'


        adb_command = f"{adb} shell ls \"{remote_dir}\""
        result = subprocess.run(adb_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print("Error: Unable to list files in the remote directory.")
            print(result.stderr)
            return


        files_cur = result.stdout
        zip_file = files_cur.split('\n')[0]
        print(f'**************{zip_file}')

        remote_path = os.path.join(remote_dir, zip_file)
        remote_path = remote_path.replace("\\", "/")
        remote_path = f"\"{remote_path}\""


        safe_zip_file = zip_file.replace(" ", "_").replace(":", "_")
        local_path = os.path.join(local_dir, safe_zip_file)
        local_path = local_path.replace("\\", "/")


        os.makedirs(local_dir, exist_ok=True)

        local_path = f"\"{local_path}\""


        pull_command = f"{adb} pull {remote_path} {local_path}"
        pull_result = subprocess.run(pull_command, shell=True, capture_output=True, text=True)


        print("STDOUT:", pull_result.stdout)
        print("STDERR:", pull_result.stderr)
        if pull_result.returncode != 0:
            print("Error pulling file.")
            return
        else:
            print(f"File pulled successfully to: {local_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def collect_results(activity, appname, accessbility_folder, results_outputs):


    scanner_pkg = 'com.google.android.apps.accessibility.auditor'
    print ('Collecting scan results from device...')

    # To save issues and screenshot temporarily in order to rename.
    tmp_folder = os.path.join(accessbility_folder, tmp_dir).replace(os.sep, '/')


    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)


    issue_path = os.path.join(results_outputs, appname, 'issues')
    if not os.path.exists(issue_path):
        os.makedirs(issue_path)

    remote_directory = "/data/data/com.google.android.apps.accessibility.auditor/cache/export"
    local_directory = 'C:/Users/Administrator/Desktop/yjs/x-bot/Xbot-main/results/emulator-5554'# tmp_folder


    adb_pull_zip_from_device(remote_directory, local_directory)


    folder_path = 'C:/Users/Administrator/Desktop/yjs/x-bot/Xbot-main/results/emulator-5554/'


    files = os.listdir(folder_path)



    for file in files:
        print(file)


    if os.path.exists(folder_path):
        for zip_file in os.listdir(folder_path):
            if zip_file.endswith('.zip'):

                target_path = os.path.join(issue_path,f'{activity}.zip')

                source_path = os.path.join(folder_path,zip_file)

                target_dir = os.path.dirname(target_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                shutil.move(source_path,target_path)

    clean_tmp_folder(folder_path)


    # if os.path.exists(os.path.join(issue_path, activity+'.zip')):
    #     unzip(os.path.join(issue_path, activity+'.zip'), activity)
    if os.path.exists(os.path.join(issue_path, f"{activity}.zip")):
        # unzip(os.path.join(issue_path, f"{activity}.zip").replace(os.sep, '/'), activity)
        zip_file = os.path.join(issue_path,f'{activity}.zip')
        unzip(zip_file,activity)

    '''Pull screenshot and rename'''

    screenshot_path = os.path.join(results_outputs, appname, 'screenshot').replace(os.sep, '/')
    if not os.path.exists(screenshot_path):
        os.makedirs(screenshot_path)

    pull_screenshots = "adb.exe pull /data/data/%s/files/screenshots/ %s" % (scanner_pkg, tmp_folder)
    os.system(pull_screenshots)

    for png in os.listdir(tmp_folder):
        if not png.endswith('thumbnail.png'):
            # os.system('mv "%s/%s" "%s/%s"'%(tmp_folder,png,screenshot_path,activity))
            if os.path.exists(os.path.join(screenshot_path, activity).replace(os.sep, '/')):
                shutil.rmtree(os.path.join(screenshot_path, activity).replace(os.sep, '/'))
            os.rename(os.path.join(tmp_folder, png).replace(os.sep, '/'), os.path.join(screenshot_path, activity).replace(os.sep, '/'))
    clean_tmp_folder(tmp_folder)

    # clean_results = adb + ' shell rm -rf /data/data/%s/cache/export/' % (scanner_pkg)
    # os.system(clean_results)

    # clean_screenshots = adb + ' shell rm -rf /data/data/%s/files/screenshots' % (scanner_pkg)
    # os.system(clean_screenshots)

    clean_results = "adb.exe shell rm -rf /data/data/%s/cache/export/" % (scanner_pkg)
    os.system(clean_results)

    clean_screenshots = "adb.exe shell rm -rf /data/data/%s/files/screenshots" % (scanner_pkg)
    os.system(clean_screenshots)


def check_current_screen():

    adb = 'adb.exe'

    current_activity = subprocess.getoutput(adb + " shell dumpsys activity activities | findstr mResumedActivity")


    error_logs = subprocess.getoutput(adb + " logcat -t 100 | findstr Error")
    exception_logs = subprocess.getoutput(adb + " logcat -t 100 | findstr Exception")


    if 'Error:' in error_logs or 'Exception:' in exception_logs:
        return False

    if 'com.android.launcher3' in current_activity:
        return False

    return True


def check_current_screen_new(activity, appname, results_outputs):
    #dump xml check whether it contains certain keywords:
    #    has stopped, isn't responding, keeps stopping, DENY, ALLOW
    
    keywords = ['has stopped', 'isn\'t responding', 'keeps stopping']

    #dump xml and check
    layout_path = os.path.join(results_outputs, appname, 'layouts')
    if not os.path.exists(layout_path):
        os.makedirs(layout_path)

    # Replace adb with the correct path to adb.exe if needed
    adb = 'adb.exe'  # Make sure adb.exe is in your PATH or provide full path here

    os.system(f'{adb} shell uiautomator dump /sdcard/{activity}.xml')

    time.sleep(2)
    # authorization
    os.system(f'{adb} shell input tap 650 1100')


    time.sleep(2)
    # start now
    os.system(f'{adb} shell input tap 845 1270')

    time.sleep(3)

    pull_xml = f'{adb} pull /sdcard/{activity}.xml {layout_path}'
    os.system(pull_xml)

    clean_xml = f'{adb} shell rm /sdcard/{activity}.xml'
    os.system(clean_xml)

    # check whether it crashes
    layout_path = os.path.join(layout_path, f'{activity}.xml')
    for word in keywords:
        result = subprocess.getoutput(f'findstr "{word}" {layout_path}')
        if result:
            # if crash, remove xml from layout folder
            os.remove(layout_path)
            return 'abnormal'

    # check whether it is a permission dialog
    if subprocess.getoutput(f'findstr /i "ALLOW" {layout_path}') and subprocess.getoutput(
            f'findstr /i "DENY" {layout_path}'):
        os.system(f'{adb} shell input tap 780 1080')  # tap ALLOW
        time.sleep(2)
        cmd = f'{adb} shell dumpsys activity activities | findstr mResumedActivity'
        cmdd = f'{adb} shell dumpsys activity activities | findstr mFocusedActivity'
        if not 'com.android.launcher3' in subprocess.getoutput(
                cmd) and not 'com.android.launcher3' in subprocess.getoutput(cmdd):
            return 'normal'
        else:
            os.remove(layout_path)
            return 'abnormal'

    cmd = f'{adb} shell dumpsys activity activities | findstr mResumedActivity'
    cmdd = f'{adb} shell dumpsys activity activities | findstr mFocusedActivity'
    if not 'com.android.launcher3' in subprocess.getoutput(cmd) and not 'com.android.launcher3' in subprocess.getoutput(
            cmdd):
        return 'normal'
    else:
        os.remove(layout_path)
        return 'abnormal'


def explore(activity, appname, results_folder, results_outputs):

    current = check_current_screen_new(activity, appname, results_outputs)
    print(current)
    if current == 'abnormal':
        # click home and click 'ok' if crashes (two kinds of 'ok's)
        os.system(f'{adb} shell input tap 540 1855')
        time.sleep(2)

        return

    if current == 'normal':
        scan_and_return()
        collect_results(activity, appname, results_folder, results_outputs)

    os.system(f'{adb} shell input keyevent HOME')
    time.sleep(4)

def clean_logcat():
    adb = 'adb.exe'
    cmd_clean = adb + ' logcat -c'

    try:

        result = subprocess.run(cmd_clean, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        print("Standard Output:", result.stdout)
        print("Standard Error:", result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
    except KeyboardInterrupt:
        print("Process interrupted.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def init_d(activity, d):
    d[activity] = {}
    d[activity]['actions'] = ''
    d[activity]['category'] = ''

    return d



def extract_activity_action(path):
    d = {}

    try:

        tree = ET.parse(path)
        root = tree.getroot()


        namespaces = {'android': 'http://schemas.android.com/apk/res/android'}


        for activity in root.findall(".//application//activity", namespaces):
            activity_name = activity.get("{http://schemas.android.com/apk/res/android}name")

            print(f"Found activity: {activity_name}")


            if activity_name is None:
                continue


            if activity_name.startswith('.'):
                activity_name = used_pkg_name + activity_name


            if activity_name not in d:
                d[activity_name] = []

            for intent_filter in activity.findall("intent-filter"):
                action_category_pair = ['', '']

                action = intent_filter.find("action")
                if action is not None:
                    action_category_pair[0] = action.get("{http://schemas.android.com/apk/res/android}name")

                category = intent_filter.find("category")
                if category is not None:
                    action_category_pair[1] = category.get("{http://schemas.android.com/apk/res/android}name")

                if action_category_pair[0] or action_category_pair[1]:
                    print(f"Action: {action_category_pair[0]}, Category: {action_category_pair[1]}")
                    d[activity_name].append(action_category_pair)

    except Exception as e:
        print(f"Error parsing manifest: {e}")

    print(f"Extracted activities: {d}")

    return d

def get_full_activity(component):
    '''get activity name, component may have two forms:
            1. com.google.abc/com.google.abc.mainactivity
            2. com.google.abc/.mainactivity
    '''
    act = component.split('/')[1]
    if act.startswith('.'):
        activity = component.split('/')[0]+act
    else:
        activity = act

    return activity

def convert(api, key, extras):
    if api == 'getString' or api == 'getStringArray':
        extras = extras + ' --es ' + key + ' test'
    if api == 'getInt' or api == 'getIntArray':
        extras = extras + ' --ei ' + key + ' 1'
    if api == 'getBoolean' or api == 'getBooleanArray':
        extras = extras + ' --ez ' + key + ' False'
    if api == 'getFloat' or api == 'getFloatArray':
        extras = extras + ' --ef ' + key + ' 0.1'
    if api == 'getLong' or api == 'getLongArray':
        extras = extras + ' --el ' + key + ' 1'
    return extras

def get_act_extra_paras(activity):
    for line in open(act_paras_file,'r').readlines():
        if line.strip() == '':
            continue
        if line.split(":")[0] == activity:
            if line.split(":")[1].strip() == '':
                return ''
            else:
                paras = line.split(':')[1].strip()
                extras = ''
                for each_para in paras.split(';'):
                    if '__' in each_para:
                        # api may refer to getString, getInt, ....
                        api = each_para.split('__')[0]
                        key = each_para.split('__')[1]
                        extras = convert(api, key, extras)
                return extras

def startAct(component, action, cate, appname, results_folder, results_outputs):

    clean_logcat()

    # cmd = adb + ' shell am start -S -n %s' % component
    adb = 'adb.exe'
    cmd = f'{adb} shell am start -S -n {component}'

    if not action == '':
        cmd = cmd + ' -a ' + action
    if not cate == '':
        cmd = cmd + ' -c ' + cate

    activity = get_full_activity(component)
    extras = get_act_extra_paras(activity)

    if extras != None:
        cmd = cmd + ' ' + extras
    os.system(cmd)
    time.sleep(3)

    return explore(activity, appname, results_folder, results_outputs)

# def save_activity_to_csv(accessbility_folder, app_name,  pkg, all_activity_num):
#     csv_file = os.path.join(accessbility_folder, 'log.csv')
#     csv.writer(open(csv_file,'ab')).writerow((app_name, pkg, all_activity_num))

# ('apk_name', 'pkg_name', 'all_act_num', 'launched_act_num','act_not_launched','act_num_with_issue')
def save_activity_to_csv(results_folder, apk_name, all_act_num, launched_act_num, act_not_launched, act_num_with_issue):
    csv_file = os.path.join(results_folder, 'log.csv')
    csv.writer(open(csv_file, 'a')).writerow((apk_name, used_pkg_name, all_act_num, launched_act_num, act_not_launched, act_num_with_issue))

def parseManifest(new_apkpath, apk_name, results_folder, decompilePath, results_outputs):

    print ("Parsing " + apk_name)

    if not os.path.exists(new_apkpath):
        print ("cannot find the decomplied app: " + apk_name)
        return

    manifestPath = os.path.join(decompilePath, apk_name, "AndroidManifest.xml")

    if not os.path.exists(manifestPath):
        print ("there is no AndroidManifest file: " + apk_name)
        return

    # format of pairs: {activity1: {actions: action1, category: cate1 }}
    print(f'manifestPath = {manifestPath}')
    pairs = extract_activity_action(manifestPath)

    all_activity_num = len(pairs.keys())
    print(all_activity_num)

    for activity, other in pairs.items():
        print(activity)
        component = defined_pkg_name + '/' + activity
        flag = 0
        for s in other:
            action = s[0]
            category = s[1]
            if action != 0 or category != 0:
                flag = 1

            status = startAct(component, action, category, apk_name, results_folder, results_outputs)

            if status =='normal':
                break


        if flag == 0:
            startAct(component, '', '', apk_name, results_folder, results_outputs)

    if not os.path.exists(results_outputs + '/' + apk_name + '/screenshot'):

        return

    get_activity_statistics(results_outputs, apk_name, all_activity_num, results_folder)

def count_files_in_directory(directory):
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])


def get_activity_statistics(results_outputs, apk_name, all_activity_num, results_folder):

    screenshot_dir = os.path.join(results_outputs, apk_name, 'screenshot')
    launched_act_num = count_files_in_directory(screenshot_dir)

    act_not_launched = all_activity_num - launched_act_num


    issues_dir = os.path.join(results_outputs, apk_name, 'issues')
    act_num_with_issue = count_files_in_directory(issues_dir)


    save_activity_to_csv(results_folder, apk_name, all_activity_num, launched_act_num, act_not_launched,
                         act_num_with_issue)

    print(issues_dir)

def get_package_name(apk_path):
    cmd = f"aapt dump badging {apk_path}"
    result = subprocess.getoutput(cmd)

    match = re.search(r"package: name='([^']+)'", result)

    if match:
        return match.group(1)
    else:
        return None

def get_pkgname(apk_path):
    global defined_pkg_name
    global used_pkg_name


    defined_pkg_name = get_package_name(apk_path)
    print(f'defined_pkg_name = {defined_pkg_name}')


    cmd = f'aapt dump badging {apk_path}'
    aapt_output = subprocess.getoutput(cmd)


    launcher_match = re.search(r"launchable-activity:'([^\']+)'", aapt_output)
    if launcher_match:
        launcher = launcher_match.group(1)
        if launcher.startswith(".") or defined_pkg_name in launcher or launcher == '':
            used_pkg_name = defined_pkg_name
        else:

            used_pkg_name = launcher.split('/')[0]
    else:
        used_pkg_name = defined_pkg_name


def remove_folder(apkname, decompilePath):
    folder = os.path.join(decompilePath, apkname)
    if not os.path.exists(folder):
        return
    for f in os.listdir(folder):
        if not f == 'AndroidManifest.xml':
            rm_path = os.path.join(folder, f)
            if os.path.isdir(rm_path):
                shutil.rmtree(rm_path)
            else:
                os.remove(rm_path)

def exploreActivity(new_apkpath, apk_name, results_folder, emulator, tmp_file, storydroid):

    global adb
    adb = "adb -s %s"%(emulator)


    global tmp_dir
    # tmp_file = os.path.join(results_folder, emulator).replace(os.sep, '/') # tmp file for parallel execution
    tmp_dir = tmp_file

    global act_paras_file
    act_paras_file = storydroid

    decompilePath = os.path.join(results_folder, "apktool")  # Decompiled app path (apktool handled)
    results_outputs = os.path.join(results_folder, "outputs")
    installErrorAppPath = os.path.join(results_folder, "install-error-apks")

    if not os.path.exists(decompilePath):
        os.makedirs(decompilePath)
    if not os.path.exists(results_outputs):
        os.makedirs(results_outputs)
    if not os.path.exists(installErrorAppPath):
        os.makedirs(installErrorAppPath)

    ### The pkg is the real pkg
    result = installAPP(new_apkpath, apk_name, results_folder)



    if result == 'Failure':
        copy_org_apk = f"move {new_apkpath} {installErrorAppPath}"
        subprocess.getoutput(copy_org_apk)
        return

    parseManifest(new_apkpath, apk_name, results_folder, decompilePath, results_outputs)
    print ("%s parsing fininshed!"%new_apkpath)

    uninstallApp(defined_pkg_name)
