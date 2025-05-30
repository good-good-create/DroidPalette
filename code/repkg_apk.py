'''
Authors: Sen Chen and Lingling Fan
input: an apk
output: a repackaged apk
'''
import os
import shutil
import subprocess
import signal
import time
import pyautogui
from sys import stdin
import threading
from adodbapi.process_connect_string import process
from numpy.distutils.lib2def import output_def

#keyPath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "coolapk.keystore")  # pwd: 123456, private key path
keyPath = r'E:\app-sign\mykeystore.jks'

TIMEOUT = 10


def run_command(cmd):
    print("decompiling...")
    os.system(cmd)


def decompile(eachappPath, decompileAPKPath):
    print("decompiling...")
    timeout = 10

    apktool_path = 'D:/Apktool/apktool.bat'
    cmd = [apktool_path, 'd', eachappPath, '-f', '-o', decompileAPKPath]


    try:

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)


        print(result.stdout)
        print(result.stderr)

        print("Decompile finished.")
    except subprocess.TimeoutExpired:
        print(f"Decompile process timed out after {timeout} seconds.")
        return  # 超时则跳过，避免继续执行
    except Exception as e:
        print(f"Error occurred: {e}")
        return  # 其他异常，退出函数



def modifyManifestAgain(line_num, decompileAPKPath):
    # in order to fix an error
    ManifestPath = os.path.join(decompileAPKPath, "AndroidManifest.xml")
    lines = open(ManifestPath,'r').readlines()
    if '@android' in lines[line_num-1]:
        #lines[line_num-1].replace('@android','@*android')
        lines[line_num-1] = lines[line_num-1].split('@android')[0] + '@*android' + lines[line_num-1].split('@android')[1]
    open(ManifestPath,'w').writelines(lines)

def recompile(decompileAPKPath):
    print("decompiling...")
    timeout = 10

    apktool_path = 'D:/Apktool/apktool.bat'
    # cmd = [apktool_path, 'd', eachappPath, '-f', '-o', decompileAPKPath]
    cmd = f"{apktool_path} b {decompileAPKPath}"

    try:

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)

        print(result.stdout)
        print(result.stderr)

        print("recompile finished.")
    except subprocess.TimeoutExpired:
        print(f"recompile process timed out after {timeout} seconds.")
        return
    except Exception as e:
        print(f"Error occurred: {e}")
        return


def sign_apk(apk_name, decompileAPKPath, repackagedAppPath):

    repackName = apk_name + '.apk'
    resign_appName = apk_name + "_sign" + '.apk'
    repackAppPath = os.path.join(decompileAPKPath,'dist',repackName)
    sign_apk_path = os.path.join(repackagedAppPath,resign_appName)
    keyPath = r'E:\app-sign\mykeystore.jks'

    cmd = [
        "C:/Users/Administrator/AppData/Local/Android/Sdk/build-tools/35.0.0/apksigner.bat",
        'sign',
        '--ks', keyPath,
        '--out', sign_apk_path,
        repackAppPath
    ]

    try:
        result = subprocess.run(
            cmd,
            input = '123456\n',
            text = True,
            capture_output=True
        )

        print(f'stdout : {result.stdout}')
        print(f'stderr : {result.stderr}')

        if result.returncode == 0:
            print('APK signed successfully!')
            return "success"
        else:
            print('APK signed failed!')
            return "fail"
    except Exception as e:
        print(f'found error : {e}')
        return "fail"

def rename(apk_name, repackagedAppPath):
    repackaged_apk_path = os.path.join(repackagedAppPath, apk_name + ".apk")
    sign_apk_path = os.path.join(repackagedAppPath, apk_name + "_sign" + ".apk")


    if os.path.exists(repackaged_apk_path):
        print(f"File {repackaged_apk_path} already exists. Removing it.")
        os.remove(repackaged_apk_path)

    os.rename(sign_apk_path, repackaged_apk_path)
    print(f"Renamed {sign_apk_path} to {repackaged_apk_path}")

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

def addExportedTrue(line):
    if 'exported="true"' in line:
        return line
    if 'exported="false"' in line:
        return line.replace('exported="false"', 'exported="true"')
    if not 'exported' in line:
        return '<activity exported="true" ' + line.split('<activity ')[1]

def modifyManifest_00(decompileAPKPath):
    newlines = []
    ManifestPath = os.path.join(decompileAPKPath, "AndroidManifest.xml")

    if not os.path.exists(ManifestPath):
        return "NoManifest"
    else:
        flag = 0
        for line in open(ManifestPath,'r').readlines():
            if line.strip().startswith('<activity '):
                line = addExportedTrue(line)
                newlines.append(line)
            else:
                newlines.append(line)
        open(ManifestPath,'w',encoding='utf-8').writelines(newlines)

def startRepkg(apk_path, apkname, results_folder, config_folder):
    global keyPath


    noManifestAppPath = os.path.join(results_folder, "no-manifest-apks")
    buildErrorAppPath = os.path.join(results_folder, "build-error-apks")
    signErrorAppPath = os.path.join(results_folder, "sign-error-apks")
    decompilePath = os.path.join(results_folder, "apktool")  # decompiled app path (apktool handled)
    repackagedAppPath = os.path.join(results_folder, "repackaged")  # store the repackaged apps

    if not os.path.exists(noManifestAppPath):
        os.makedirs(noManifestAppPath)

    if not os.path.exists(buildErrorAppPath):
        os.makedirs(buildErrorAppPath)

    if not os.path.exists(signErrorAppPath):
        os.makedirs(signErrorAppPath)

    if not os.path.exists(decompilePath):
        os.makedirs(decompilePath)

    if not os.path.exists(repackagedAppPath):
        os.makedirs(repackagedAppPath)

    decompileAPKPath = os.path.join(decompilePath, apkname)

    decompile(apk_path, decompileAPKPath)

    msg = modifyManifest_00(decompileAPKPath)

    if msg == "NoManifest":

        copy_org_apk = "mv %s %s"%(apk_path, repackagedAppPath)
        subprocess.getoutput(copy_org_apk)

        copy_org_apk = "mv %s %s"%(apk_path, noManifestAppPath)
        subprocess.getoutput(copy_org_apk)
        return 'no manifest file'

    recompileInfo = recompile(decompileAPKPath)


    builtApk = True

    if not builtApk:
        # Copy original app to repackage folder
        copy_org_apk = "mv %s %s"%(apk_path, repackagedAppPath)
        subprocess.getoutput(copy_org_apk)

        # Copy original app to build-error-apks
        copy_org_apk = "mv %s %s"%(apk_path, buildErrorAppPath)
        subprocess.getoutput(copy_org_apk)

        return 'build error'

    print ("signing...")
    # Sign the modified apk
    signlabel = sign_apk(apkname, decompileAPKPath, repackagedAppPath)

    if signlabel == "fail":
        # Copy original app to repackage folder
        copy_org_apk = "mv %s %s"%(apk_path, repackagedAppPath)
        subprocess.getoutput(copy_org_apk)

        # Copy original app to build-error-apks
        copy_org_apk = "mv %s %s"%(apk_path, signErrorAppPath)
        subprocess.getoutput(copy_org_apk)

        return 'sign error'

    move_apk(apk_path, repackagedAppPath)


    rename(apkname, repackagedAppPath)



def move_apk(apk_path, repackagedAppPath):
    try:
        dest_path = os.path.join(repackagedAppPath, os.path.basename(apk_path))
        shutil.move(apk_path, dest_path)
        print(f"APK moved to {dest_path}")
    except Exception as e:
        print(f"Error occurred while moving APK: {e}")