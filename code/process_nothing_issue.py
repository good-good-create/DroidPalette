import xml.etree.ElementTree as ET
import os
from idlelib.tree import TreeItem


def get_application_theme(main_path):

    tree = ET.parse(main_path)
    root = tree.getroot()

    application = root.find(".//application")
    if application is not None:
        theme = application.get("{http://schemas.android.com/apk/res/android}theme")
        return theme
    else:
        return None


def change_act_theme(main_path,act_name,new_theme):

    tree = ET.parse(main_path)
    root = tree.getroot()

    for activity in root.findall(".//application//activity"):

        activity_name = activity.get("{http://schemas.android.com/apk/res/android}name")

        if activity_name.endswith(act_name):
            activity.set("{http://schemas.android.com/apk/res/android}theme",new_theme)

    tree.write(main_path,encoding='utf-8',xml_declaration=True)

def insert_toolbar_style(styles_path,parent_name,new_color,app_theme_name,toolbar_name):

    tree = ET.parse(styles_path)
    root = tree.getroot()

    app_theme = None
    for style in root.findall("style"):
        if style.get("name") == app_theme_name:
            app_theme = style
            break

    if app_theme is not None:

        toolbar_item_exists = False
        for item in app_theme.findall("item"):
            if item.get("name") == 'toolbarNavigationButtonStyle':
                toolbar_item_exists = True
        if not toolbar_item_exists:

            item1 = ET.Element("item", name="toolbarNavigationButtonStyle")
            item1.text = f"@style/{toolbar_name}"
            app_theme.append(item1)
    else:
        app_theme = ET.Element("style", {"name": app_theme_name, "parent": parent_name})
        item1 = ET.Element("item",{"name":"toolbarNavigationButtonStyle"})
        item1.text = f"@style/{toolbar_name}"
        app_theme.append(item1)
        root.append(app_theme)

    toolbar_style = None
    for style in root.findall("style"):
        if style.get("name") == toolbar_name:
            toolbar_style = style
            break

    if toolbar_style is not None:
        tint_item_exists = False
        for item in toolbar_style.findall("item"):
            if item.get("name") == "android:tint" and item.text == new_color:
                tint_item_exists = True
                break

        if not tint_item_exists:
            item2 = ET.Element("item",{"name" : "android:tint"})
            item2.text = new_color
            toolbar_style.append(item2)

    else:

        toolbar_style = ET.Element("style", {"name" : toolbar_name})
        item2 = ET.Element("item", {"name": "android:tint"})
        item2.text = new_color
        toolbar_style.append(item2)
        root.append(toolbar_style)

    tree.write(styles_path,encoding='utf-8',xml_declaration=True)

def process_nothing(act_name,report_path,decomp_path,no_id_text_issue,app_name,component_with_issue):

    app_report = os.path.join(report_path,app_name)
    layout_path = os.path.join(app_report,"layouts",f"{act_name}.xml")
    main_path = os.path.join(decomp_path,"AndroidManifest.xml")


    act_name = act_name.split('.')[-1]

    app_theme_name = act_name + '_new'
    toolbar_name = act_name + '_CustomToolbarNavigationButtonStyle'
    new_theme = "@style/" + act_name + "_new"

    change_act_theme(main_path,act_name,new_theme)

    styles_path = os.path.join(decomp_path,"res","values","styles.xml")

    parent_name = get_application_theme(main_path)
    new_color = "#ffffff"

    dict_value = component_with_issue[('', '')]
    third_element = dict_value[2]
    new_color = third_element[0][1]
    print(f'new_color为{new_color}')

    insert_toolbar_style(styles_path, parent_name, new_color, app_theme_name, toolbar_name)



