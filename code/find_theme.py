import os.path
import xml.etree.ElementTree as ET
from idlelib.iomenu import encoding
from multiprocessing.process import parent_process

from lxml import etree



namespaces = {
    'android': 'http://schemas.android.com/apk/res/android'
}

def parse_manifest(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


def find_theme_for_label(manifest_root,label_name):

    manifest_root = parse_manifest(manifest_root)
    theme_list = []

    application = manifest_root.findall(f".//application[@android:label='{label_name}']", namespaces)
    print(f'application:{application}')
    if application:
        for app in application:
            theme = app.attrib.get("{http://schemas.android.com/apk/res/android}theme")
            if theme:
                theme_name = theme.replace('@style/','')
                theme_list.append(theme_name)


    for activity in manifest_root.findall(f".//activity[@android:label='{label_name}']", namespaces):
        theme = activity.attrib.get("{http://schemas.android.com/apk/res/android}theme")
        if theme:
            theme_name = theme.replace('@style/','')
            theme_list.append(theme_name)

    return theme_list

def ensure_attr_in_xml(attr_path,attr_name,attr_format):
    attr_line = f'<attr name="{attr_name}" format="{attr_format}" />'

    if not os.path.exists(attr_path):
        os.makedirs(os.path.dirname(attr_path),exist_ok=True)
        with open(attr_path,'w',encoding='utf-8') as file:
            file.write('<resources>\n</resources>')

    with open(attr_path,'r',encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        if f'<attr name="{attr_name}"' in line:
            return

    for i,line in enumerate(lines):
        if '<resources>' in line:
            insert_index = i + 1
            break
    else:
        return

    lines.insert(insert_index,f'    {attr_line}\n')
    with open(attr_path,'w',encoding='utf-8') as file:
        file.writelines(lines)

def insert_toolbar_style(style_path,new_color,decomp_path):
    try:
        tree = etree.parse(style_path)
        root = tree.getroot()

        existing_toolbar_item = root.xpath("//item[@name='toolbarStyle']")

        if existing_toolbar_item:
            parent_style = existing_toolbar_item[0].text

        else:
            # parent_style = "@style/Widget.MaterialComponents.Toolbar"
            parent_style = "@android:style/Widget.Holo.Light.ActionBar"

        existing_style = root.xpath("//style[@name = 'ToolbarStyle']")
        if existing_style:
            return

        toolbar_style = etree.Element("style",name="ToolbarStyle",parent = parent_style)


        attr_path = os.path.join(decomp_path,"res","values","attrs.xml")
        attr_name = 'titleTextColor'
        attr_format = 'color'
        ensure_attr_in_xml(attr_path,attr_name,attr_format)

        title_text_color = etree.Element("item",name = "titleTextColor")
        title_text_color.text = new_color

        toolbar_style.append(title_text_color)
        root.append(toolbar_style)

        tree.write(style_path,pretty_print = True,xml_declaration=True,encoding='utf-8')
    except Exception as e:
        print(f'Errot:{e}')




def insert_item(style_path,theme_name):
    tree = etree.parse(style_path)
    root = tree.getroot()


    theme = None
    for style in root.findall("style"):
        name = style.get("name")
        if name == theme_name:
            theme = style
            break

    if theme is None:
        print(f"Don't find {theme_name}!")
        return

    existing_item = None
    for item in theme.findall("item"):
        if item.get("name") == "toolbarStyle":
            existing_item = item
            break

    if existing_item is not None:
        return

    toolbar_style_item = etree.Element("item",name = "toolbarStyle")
    toolbar_style_item.text = "@style/ToolbarStyle"


    theme.append(toolbar_style_item)


    tree.write(style_path,pretty_print = True,xml_declaration = True,encoding = "utf-8")


def do_modify_title(theme_list,style_path,new_color,decomp_path):


    for theme_name in theme_list:

        insert_item(style_path,theme_name)

    insert_toolbar_style(style_path, new_color,decomp_path)
