import os
import subprocess
import shutil
from sre_parse import parse

from PIL import Image
from lxml import etree as ET
from pygetwindow import pointInRect

import find_theme

candidate_att_text = ['{http://schemas.android.com/apk/res/android}textColor','{http://schemas.android.com/apk/res/android}textColorHint','{http://schemas.android.com/apk/res/android}textColorLink',
                      '{http://schemas.android.com/apk/res/android}focusedSearchResultHighlightColor','{http://schemas.android.com/apk/res/android}searchResultHighlightColor','{http://schemas.android.com/apk/res/android}shadowColor',
                      '{http://schemas.android.com/apk/res/android}textColorHighlight','{http://schemas.android.com/apk/res/android}cacheColorHint ','{http://schemas.android.com/apk/res/android}focusedMonthDateColor',
                      '{http://schemas.android.com/apk/res/android}unfocusedMonthDateColor','{http://schemas.android.com/apk/res/android}weekNumberColor ','{http://schemas.android.com/apk/res/android}calendarTextColor',
                      '{http://schemas.android.com/apk/res/android}dayOfWeekBackground','{http://schemas.android.com/apk/res/android}headerBackground ','{http://schemas.android.com/apk/res/android}yearListSelectorColor',
                      '{http://schemas.android.com/apk/res/android}subtitleTextColor']
candidate_att_image = ['{http://schemas.android.com/apk/res/android}tint','{http://schemas.android.com/apk/res/android}backgroundTint','{http://schemas.android.com/apk/res/android}drawableTint',
                       '{http://schemas.android.com/apk/res/android}thumbTint','{http://schemas.android.com/apk/res/android}drawableTintMode','{http://schemas.android.com/apk/res/android}tickMarkTint',
                       '{http://schemas.android.com/apk/res/android}hand_hourTint','{http://schemas.android.com/apk/res/android}hand_minuteTint','{http://schemas.android.com/apk/res/android}hand_secondTint',
                       '{http://schemas.android.com/apk/res/android}weekSeparatorLineColor','{http://schemas.android.com/apk/res/android}checkMarkTint','{http://schemas.android.com/apk/res/android}buttonTint',
                       '{http://schemas.android.com/apk/res/android}childDivider','{http://schemas.android.com/apk/res/android}divider','{http://schemas.android.com/apk/res/android}indeterminateTint']
title_att = 'titleTextColor'

def do_button_modify(layout_file,component_id_string,new_color,text_cur_seq):

    if not layout_file:
        return None


    tree = ET.parse(layout_file)
    root = tree.getroot()



    ns = {'android': 'http://schemas.android.com/apk/res/android'}


    for elem in root.iter():

        text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')

        if text_value and text_value == f'@string/{component_id_string}':

            attr_name = candidate_att_text[text_cur_seq].split('}', 1)[-1]

            if candidate_att_text[text_cur_seq] in elem.attrib:
                elem.attrib[candidate_att_text[text_cur_seq]] = new_color
            else:
                elem.set(candidate_att_text[text_cur_seq],new_color)


            tree.write(layout_file,encoding= 'utf-8',xml_declaration=True)
            return True

    return False


def do_title_modify(decomp_path, component_id_string, new_color):
    cur_id = component_id_string[0]
    cur_text = component_id_string[1]
    if cur_id == 'app_name' or cur_text == 'app_name':
        styles_xml_path = os.path.join(decomp_path, 'res', 'values', 'styles.xml')

        if not os.path.exists(styles_xml_path):
            print(f'{styles_xml_path} not found!')
            return

        tree = ET.parse(styles_xml_path)
        root = tree.getroot()

        for style in root.findall("style"):
            for item in style.findall('item'):
                item_name = item.attrib.get('name')
                if item_name == 'titleTextColor':
                    item.text = new_color
                    tree.write(styles_xml_path, encoding='utf-8', xml_declaration=True)
                    return


def do_image_modify(layout_file,component_id_string,new_color,image_seq,component_with_issue):

    if not layout_file:
        return None

    if image_seq > 2:
        return None

    tree = ET.parse(layout_file)
    root = tree.getroot()

    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    target_attribute = candidate_att_image[image_seq].split('}', 1)[-1]

    for elem in root.iter():

        id_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}id')
        text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')

        if id_value and (id_value == f'@+id/{component_id_string[0]}' or id_value == f'@id/{component_id_string[0]}'):

            attr_name = candidate_att_image[image_seq].split('}',1)[-1]

            if candidate_att_image[image_seq] in elem.attrib:

                elem.attrib[candidate_att_image[image_seq]] = new_color

            else:

                elem.set(candidate_att_image[image_seq],new_color)

                component_data = list(component_with_issue[component_id_string])
                component_data[3] = 1
                component_with_issue[component_id_string] = tuple(component_data)

            tree.write(layout_file,encoding = 'utf-8',xml_declaration=True)
            return True

        elif text_value and text_value == f'@string/{component_id_string[1]}':

            attr_name = candidate_att_image[image_seq].split('}', 1)[-1]
            if candidate_att_image[image_seq] in elem.attrib:

                elem.attrib[candidate_att_image[image_seq]] = new_color

            else:
                elem.set(candidate_att_image[image_seq],new_color)
                component_data = list(component_with_issue[component_id_string])
                component_data[3] = 1
                component_with_issue[component_id_string] = tuple(component_data)


            tree.write(layout_file,encoding= 'utf-8',xml_declaration=True)
            return True

        parent_elem = elem.getparent()
        while parent_elem is not None:
            if f"{{http://schemas.android.com/apk/res/android}}{target_attribute}" in parent_elem.attrib:

                parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                return True
            parent_elem = parent_elem.getparent()

    return False



def do_theme_modify(decomp_path,component_id_string,new_color):
     cur_id = component_id_string[0]
     cur_text = component_id_string[1]
     if cur_id == 'title':
         styles_xml_path = os.path.join(decomp_path,'res','values','styles.xml')

         if not os.path.exists(styles_xml_path):
             print(f'{styles_xml_path} not found!')
             return

         tree = ET.parse(styles_xml_path)
         root = tree.getroot()

         for style in root.findall("style"):
             style_name = style.get('name')
             if style_name == 'PreferenceThemeOverlay':
                 for item in style.findall('item'):
                     item_name = item.attrib.get('name')
                     if item_name == 'preferenceCategoryTitleTextColor':
                         item.text = new_color
                         tree.write(styles_xml_path,encoding='utf-8',xml_declaration=True)
                         return
             elif style_name == 'PreferenceCategoryTitleTextStyle':
                 for item in style.findall('item'):
                     item_name = item.attrib.get('name')
                     if item_name == 'android:textColor':
                         item.text = new_color
                         tree.write(styles_xml_path,encoding='utf-8',xml_declaration=True)
                         return



def find_component_in_xml(layout_file,component_id_string):
    tree = ET.parse(layout_file)
    root = tree.getroot()

    ns = {'android':'http://schemas.android.com/apk/res/android'}

    for elem in root.iter():
        if '{http://schemas.android.com/apk/res/android}id' in elem.attrib:
            id_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}id')
            if id_value == f'@+id/{component_id_string[0]}' or id_value == f'@id/{component_id_string[0]}':
                return True

        if '{http://schemas.android.com/apk/res/android}text' in elem.attrib:
            text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')
            if text_value == f'@string/{component_id_string[1]}':
                return True
    return False

def find_xml(decomp_path,component_id_string):

    layout_xml_set = []

    layout_dir = os.path.join(decomp_path,'res','layout')

    if not os.path.exists(layout_dir):
        return []


    for root,_,files in os.walk(layout_dir):
        for file in files:
            if file.endswith('.xml'):
                layout_file = os.path.join(root,file)

                if find_component_in_xml(layout_file,component_id_string):

                    layout_xml_set.append(layout_file)


    return layout_xml_set

def modify_component(decomp_path,component_with_issue,text_seq,image_seq):
    text_flag = 0
    image_flag = 0
    if text_seq >=3 or image_seq >= 3:
        return
    for key,value in component_with_issue.items():
        component_id_string = key

        layout_file_set = find_xml(decomp_path,component_id_string)


        cur_class = component_with_issue[component_id_string][1]


        new_color = component_with_issue[component_id_string][2][0][1]


        if cur_class == 'Text contrast':
            text_flag = 1

            for layout_file in layout_file_set:
                do_text_modify_parent(layout_file,component_id_string,new_color,text_seq,component_with_issue)

            if component_id_string[0] == 'title' and text_seq == 0:
                do_theme_modify(decomp_path,component_id_string, new_color)

        else:
            image_flag = 1
            for layout_file in layout_file_set:
                do_image_modify(layout_file,component_id_string,new_color,image_seq,component_with_issue)


        if text_seq == 2 and ( component_id_string[0] == 'title' or 'title' in component_id_string[1] or 'title' in component_id_string[0] or ('setting' in component_id_string[1] and len(component_id_string[1]) < 15) or component_id_string[1] == 'app_name'):

            change_app_name_2(decomp_path, component_id_string, new_color)

        if text_seq == 2 and 'button' in component_id_string[0]:
            for layout_file in layout_file_set:
                do_button_modify(layout_file, component_id_string[1], new_color,text_cur_seq = 1)

    if text_flag == 1:
        text_seq += 1
    if image_flag == 1:
        image_seq += 1


    return text_seq,image_seq


def modify_child(decomp_path,component_with_issue):

    for key, value in component_with_issue.items():
        component_id_string = key

        layout_file_set = find_xml(decomp_path, component_id_string)
        for layout_file in layout_file_set:
            tree = ET.parse(layout_file)
            root = tree.getroot()
            direct_children = []

            for elem in root.iter():
                if 'id' in elem.attrib:
                    if component_id_string in elem.attrib['id']:
                        for child in elem:
                            if 'id' in child.attrib:
                                direct_children.append(child.attrib['id'])

            for child_id in direct_children:
                if child_id not in component_with_issue:
                    component_with_issue[child_id] = component_with_issue[component_id_string]

            if component_id_string in component_with_issue:
                del component_with_issue[component_id_string]

    return component_with_issue

def modify_component_2(decomp_path,component_with_issue,component_id_string,text_seq,image_seq,flag):

    layout_file_set = find_xml(decomp_path,component_id_string)

    cur_class = component_with_issue[component_id_string][1]

    new_color = component_with_issue[component_id_string][2][0][0]


    if cur_class == 'Text contrast':
        for layout_file in layout_file_set:

            do_text_modify_recover(layout_file,component_id_string,new_color,text_seq,flag)

    else:
        for layout_file in layout_file_set:

            do_image_modify_recover(layout_file,component_id_string,new_color,image_seq,flag)


def recompile_apk(decompileAPKPath):
    print("recompiling...")
    timeout = 10

    apktool_path = 'D:/Apktool/apktool.bat'
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

def move_apk_to_target(recomp_apk_path,target_dir):

    if not os.path.exists(recomp_apk_path):
        print(f"Directory {recomp_apk_path} does not exist！")
        return

    for filename in os.listdir(recomp_apk_path):
        file_path = os.path.join(recomp_apk_path,filename)
        name,ext = os.path.splitext(filename)

        if ext.lower() == '.apk':
            target_apk = os.path.join(target_dir,filename)

            try:
                shutil.move(file_path,target_apk)
                print(f"APK file {filename} has been moved to {target_apk}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"File {filename} is not an APK file, skipping.")



def change_app_name(decomp_path,component_id_string,new_color):
    att_id = component_id_string[0]
    label_name = component_id_string[1]
    manifest_root = os.path.join(decomp_path,"AndroidManifest.xml")
    theme_list = []

    label_name = '@string/' + label_name
    print(f'label_name : {label_name}')

    theme_list = find_theme.find_theme_for_label(manifest_root, label_name)
    print(f'theme_list : {theme_list}')


    label_name = '@string/app_name'
    theme_list = find_theme.find_theme_for_label(manifest_root, label_name)

    style_path = os.path.join(decomp_path,"res","values","styles.xml")
    find_theme.do_modify_title(theme_list, style_path, new_color,decomp_path)


def last_change_image(decomp_path,component_with_issue):

    for key,value in component_with_issue.items():
        component_id_string = key

        layout_file_set = find_xml(decomp_path,component_id_string)


        cur_class = component_with_issue[component_id_string][1]

        new_color = component_with_issue[component_id_string][2][0][1]



        if cur_class == 'Image contrast':
            for layout_file in layout_file_set:
                do_image_last(layout_file,component_id_string,new_color,decomp_path)


def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def process_png_color(image_path,output_path,new_color):
    try:
        img = Image.open(image_path).convert("RGBA")
        datas = img.getdata()


        new_data = []
        for item in datas:
            if item[3] > 0:
                new_data.append((new_color[0],new_color[1],new_color[2],item[3]))
            else:
                new_data.append(item)
        img.putdata(new_data)
        img.save(output_path,"PNG")
    except Exception as e:
        print(f"can not process : {image_path},error ：{e}")

from lxml import etree
def do_image_last(layout_file,component_id_string,new_color,decomp_path):

    res_path = os.path.join(decomp_path, "res")
    drawable_folders = [
        folder for folder in os.listdir(res_path)
        if os.path.isdir(os.path.join(res_path,folder)) and folder.startswith("drawable")
    ]

    src_list = []
    src_list = find_src(layout_file,component_id_string,src_list)
    print(f"src_list : {src_list}")
    for src in src_list:
        src = src.split('/')[-1]

        for folder in drawable_folders:
            folder = os.path.join(res_path,folder)
            for root,dirs,files in os.walk(folder):
                for file in files:
                    if file.lower() == f"{src}.xml" :
                        file_path = os.path.join(root,file)
                        try:
                            tree = etree.parse(file_path)
                            root_element = tree.getroot()

                            namespaces = {'android': 'http://schemas.android.com/apk/res/android'}

                            fill_color_elements = root_element.xpath('//*[@android:fillColor]',namespaces = namespaces)
                            for element in fill_color_elements:
                                element.set("{http://schemas.android.com/apk/res/android}fillColor",new_color)
                            tint_color_elements = root_element.xpath("//*[@android:tint]",namespaces = namespaces)
                            for element in tint_color_elements:
                                element.set("{http://schemas.android.com/apk/res/android}tint", new_color)


                            tree.write(file_path,pretty_print=True,xml_declaration = True,encoding='utf-8')

                        except Exception as e:
                            print(f"error : {e}")
                        break
                    if file.lower() == f"{src}.png":
                        file_path = os.path.join(root,file)
                        print(f"file_path:{file_path}")
                        output_path = file_path
                        rgb_color = hex_to_rgb(new_color)
                        process_png_color(file_path,output_path,rgb_color)
                        break


def find_src(layout_file,component_id_string,src_list):

    if not layout_file:
        return None

    tree = ET.parse(layout_file)
    root = tree.getroot()

    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    for elem in root.iter():

        id_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}id')
        text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')

        if id_value and (id_value == f'@+id/{component_id_string[0]}' or id_value == f'@id/{component_id_string[0]}'):
           src = elem.get("{http://schemas.android.com/apk/res/android}src")
           src_compat = elem.get("{http://schemas.android.com/apk/res-auto}srcCompat")
           if src:
               src_list.append(src)
           if src_compat:
               src_list.append(src_compat)

        elif text_value and text_value == f'@string/{component_id_string[1]}':
            src = elem.get("{http://schemas.android.com/apk/res/android}src")
            src_compat = elem.get("{http://schemas.android.com/apk/res-auto}srcCompat")
            if src:
                src_list.append(src)
            if src_compat:
                src_list.append(src_compat)

    return src_list


def do_text_modify_parent(layout_file,component_id_string,new_color,text_seq,component_with_issue):

    if not layout_file:
        return None

    tree = ET.parse(layout_file)
    root = tree.getroot()

    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    if text_seq > 2:
        return None

    target_attribute = candidate_att_text[text_seq].split('}',1)[-1]

    for elem in root.iter():

        id_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}id')
        text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')

        if id_value and (id_value == f'@+id/{component_id_string[0]}' or id_value == f'@id/{component_id_string[0]}'):

            if candidate_att_text[text_seq] in elem.attrib:
                elem.attrib[candidate_att_text[text_seq]] = new_color

            else:
                elem.set(candidate_att_text[text_seq],new_color)

                component_data = list(component_with_issue[component_id_string])
                component_data[3] = 1
                component_with_issue[component_id_string] = tuple(component_data)


            tree.write(layout_file,encoding = 'utf-8',xml_declaration=True)

            parent_elem = elem.getparent()
            while parent_elem is not None:
                if f"{{http://schemas.android.com/apk/res/android}}{target_attribute}" in parent_elem.attrib:
                    parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                    return True
                if "{http://schemas.android.com/apk/res/android}hint" in parent_elem.attrib and target_attribute == "textColorHint":

                    parent_elem.set('{http://schemas.android.com/apk/res/android}textColorHint', new_color)

                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)

                    return True
                parent_elem = parent_elem.getparent()

            return True

        elif text_value and text_value == f'@string/{component_id_string[1]}':

            if candidate_att_text[text_seq] in elem.attrib:
                elem.attrib[candidate_att_text[text_seq]] = new_color
            else:
                elem.set(candidate_att_text[text_seq],new_color)

                component_data = list(component_with_issue[component_id_string])
                component_data[3] = 1
                component_with_issue[component_id_string] = tuple(component_data)

            tree.write(layout_file,encoding= 'utf-8',xml_declaration=True)

            parent_elem = elem.getparent()
            while parent_elem is not None:
                if f"{{http://schemas.android.com/apk/res/android}}{target_attribute}" in parent_elem.attrib:

                    parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                    return True
                if "{http://schemas.android.com/apk/res/android}hint" in parent_elem.attrib and target_attribute == "textColorHint":

                    parent_elem.set('{http://schemas.android.com/apk/res/android}textColorHint', new_color)

                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)

                    return True
                parent_elem = parent_elem.getparent()

            return True

    return False

def do_text_modify_recover(layout_file,component_id_string,new_color,text_seq,flag):

    if not layout_file:
        return None


    tree = ET.parse(layout_file)
    root = tree.getroot()


    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    if text_seq > 2:
        return None

    target_attribute = candidate_att_text[text_seq].split('}',1)[-1]

    for elem in root.iter():

        id_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}id')
        text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')

        if id_value and (id_value == f'@+id/{component_id_string[0]}' or id_value == f'@id/{component_id_string[0]}'):

            if candidate_att_text[text_seq] in elem.attrib:

                if flag == 0:
                    elem.attrib[candidate_att_text[text_seq]] = new_color
                else:
                    print(f"flag : {flag}")
                    del elem.attrib[candidate_att_text[text_seq]]

            parent_elem = elem.getparent()
            while parent_elem is not None:
                if f"{{http://schemas.android.com/apk/res/android}}{target_attribute}" in parent_elem.attrib:

                    if flag == 0:
                        parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                    else:

                        parent_elem.attrib.pop(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}",None)
                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                    return True
                if "{http://schemas.android.com/apk/res/android}hint" in parent_elem.attrib and target_attribute == "textColorHint":

                    if flag == 0:
                        parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                    else:

                        parent_elem.attrib.pop(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}",None)

                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                    return True
                parent_elem = parent_elem.getparent()

            tree.write(layout_file,encoding = 'utf-8',xml_declaration=True)
            return True

        elif text_value and text_value == f'@string/{component_id_string[1]}':

            if candidate_att_text[text_seq] in elem.attrib:
                if flag == 0:
                    elem.attrib[candidate_att_text[text_seq]] = new_color
                else:
                    del elem.attrib[candidate_att_text[text_seq]]

            parent_elem = elem.getparent()
            while parent_elem is not None:
                if f"{{http://schemas.android.com/apk/res/android}}{target_attribute}" in parent_elem.attrib:

                    if flag == 0:
                        parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                    else:

                        parent_elem.attrib.pop(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}",
                                               None)
                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                    return True
                if "{http://schemas.android.com/apk/res/android}hint" in parent_elem.attrib and target_attribute == "textColorHint":

                    if flag == 0:
                        parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)
                    else:

                        parent_elem.attrib.pop(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}",
                                               None)

                    tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                    return True
                parent_elem = parent_elem.getparent()


            tree.write(layout_file,encoding= 'utf-8',xml_declaration=True)
            return True


    return False

def do_image_modify_recover(layout_file,component_id_string,new_color,image_seq,flag):

    if not layout_file:
        return None

    if image_seq > 2:
        return None

    tree = ET.parse(layout_file)
    root = tree.getroot()


    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    target_attribute = candidate_att_image[image_seq].split('}', 1)[-1]

    for elem in root.iter():

        id_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}id')
        text_value = elem.attrib.get('{http://schemas.android.com/apk/res/android}text')

        if id_value and (id_value == f'@+id/{component_id_string[0]}' or id_value == f'@id/{component_id_string[0]}'):

            attr_name = candidate_att_image[image_seq].split('}',1)[-1]

            if candidate_att_image[image_seq] in elem.attrib:

                if flag == 0:
                    elem.attrib[candidate_att_image[image_seq]] = new_color
                else:
                    del elem.attrib[candidate_att_image[image_seq]]

            tree.write(layout_file,encoding = 'utf-8',xml_declaration=True)
            return True

        elif text_value and text_value == f'@string/{component_id_string[1]}':

            attr_name = candidate_att_image[image_seq].split('}', 1)[-1]
            if candidate_att_image[image_seq] in elem.attrib:

                if flag == 0:
                    elem.attrib[candidate_att_image[image_seq]] = new_color
                else:
                    del elem.attrib[candidate_att_image[image_seq]]

            tree.write(layout_file,encoding= 'utf-8',xml_declaration=True)
            return True

        parent_elem = elem.getparent()
        while parent_elem is not None:
            if f"{{http://schemas.android.com/apk/res/android}}{target_attribute}" in parent_elem.attrib:

                parent_elem.set(f"{{http://schemas.android.com/apk/res/android}}{target_attribute}", new_color)

                tree.write(layout_file, encoding='utf-8', xml_declaration=True)
                return True
            parent_elem = parent_elem.getparent()

    return False


def change_app_name_2(decomp_path,component_id_string, new_color):
    styles_path = os.path.join(decomp_path,"res/values/styles.xml")
    if not os.path.exists(styles_path):
        raise FileNotFoundError(f'not found styles.xml')

    tree = ET.parse(styles_path)
    root = tree.getroot()

    app_theme = None
    for style in root.findall('style'):
        if style.get('name') == 'AppTheme':
            app_theme = style
            break

    if app_theme is None:
        change_app_name(decomp_path, component_id_string, new_color)
        return
        raise ValueError("apptheme not found!")

    toolbar_style = None
    for item in app_theme.findall('item'):
        if item.get('name') == 'toolbarStyle':
            toolbar_style = item
            break
    if toolbar_style is None:

        toolbar_style_name = "MyToolbarStyle"
        toolbar_style = ET.SubElement(app_theme,'item',{'name':"toolbarStyle"})
        toolbar_style.text = f'@style/{toolbar_style_name}'

        new_toolbar_style = ET.SubElement(root,'style',{'name':toolbar_style_name,'parent':'Widget.AppCompat.Toolbar'})
        ET.SubElement(new_toolbar_style, "item", {"name": "titleTextColor"}).text = new_color

    else:

        toolbar_style_name = toolbar_style.text.split("/")[-1]
        toolbar_style_definition = None
        for style in root.findall("style"):
            if style.get("name") == toolbar_style_name:
                toolbar_style_definition = style
                break

        if toolbar_style_definition is None:

            new_toolbar_style = ET.SubElement(root, "style",
                                              {"name": toolbar_style_name, "parent": "Widget.AppCompat.Toolbar"})
            ET.SubElement(new_toolbar_style, "item", {"name": "titleTextColor"}).text = new_color
        else:

            title_text_color = None
            for item in toolbar_style_definition.findall('item'):
                if item.get('name') == 'titleTextColor':
                    title_text_color = item
                    break

            if title_text_color is None:
                ET.SubElement(toolbar_style_definition,'item',{'name':'titleTextColor'}).text = new_color
            else:
                title_text_color.text = new_color

    tree.write(styles_path, encoding="utf-8", xml_declaration=True)