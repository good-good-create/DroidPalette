
import os
from pathlib import Path
import xml.etree.ElementTree as ET



def get_color_issueInfo(txt):
    color_info = []
    tempTxt = (txt.split("foreground color of ")[1]).split(" and an estimated background color of ")
    foreColor = tempTxt[0]
    backColor = tempTxt[1].split('.')[0]
    color_info.append(foreColor)
    color_info.append(backColor)
    return color_info


def get_text_by_bound(bounds,bounds_dict):
    if bounds in bounds_dict:
        return [node['text'] for node in bounds_dict[bounds]]
    return  None


def get_text_by_id(id,nodes_info):
    for node in nodes_info:
        cur_id = ''
        resource_id = node.get('resource-id','')
        # print('resource-id are as below:')
        # print(resource_id)
        if resource_id:
            parts = resource_id.split(':id/')
            # print(parts)
            if len(parts) > 1:
                cur_id = parts[-1]
            if cur_id == id:
                return node['text']

def get_all_bound(layout_path,act_name):

    nodes_info = []
    # print(layout_path)
    for file in os.listdir(layout_path):
        if file.startswith(act_name):
            file_path = os.path.join(layout_path,file)

            with open(file_path,'r', encoding = 'utf-8') as f:
                # 解析XML文件
                tree = ET.parse(f)
                root = tree.getroot()

                for node in root.iter('node'):
                    node_info = {
                        'text':node.attrib.get('text','N/A'),
                        'resource-id':node.attrib.get('resource-id','N/A'),
                        'class':node.attrib.get('class','N/A'),
                        'bounds':node.attrib.get('bounds','N/A')
                    }

                    nodes_info.append(node_info)

    bounds_dict = {}
    for node in nodes_info:
        bounds = node['bounds']

        if bounds not in bounds_dict:
            bounds_dict[bounds] = []
        bounds_dict[bounds].append(
            {
                'resource-id':node['resource-id'],
                'text':node['text'],
                'class':node['class']
            }
        )

    return nodes_info,bounds_dict




def find_issue(act_name,report_path):
    id_or_bound_list = {}
    id_or_bound_class_list = {}

    layout_path = os.path.join(report_path,"layouts")
    # print(layout_path)
    nodes_info,bounds_dict= get_all_bound(layout_path,act_name)
    # print(nodes_info)
    for file in os.listdir(report_path):

        if file.startswith('issue'):
            dir1_path = os.path.join(report_path,file)
            # print(dir1_path)
            for act in os.listdir(dir1_path):

                if act == act_name:
                    # print(act)
                    act_path = os.path.join(dir1_path,act)
                    # print(act_path)
                    for txt_file in os.listdir(act_path):

                        if txt_file.endswith(".txt"):
                            target_file_name = os.path.join(act_path,txt_file)
                            target_file_name = target_file_name.replace("\\","/")

                            with open(target_file_name,"r",encoding='utf-8') as f:
                                lis = []
                                lists = []
                                templists = []

                                for line in f:
                                    lis.append(line)


                                for li in lis:

                                    li = li.split("\n")
                                    lists.append(li[0])

                                for l in lists:
                                    if l != "":
                                        templists.append(l)

                                    else:

                                        '''
                                        Text contrast
                                        a2dp.Vol:id/pi_tv_name
                                        The item's text contrast ratio is 1.04. This ratio is based on an estimated foreground color of #FFFFFF and an estimated background color of #FAFAFA. Consider increasing this item's text contrast ratio to 3.00 or greater.
                                        '''

                                        if len(templists) >= 3 and templists[0] == 'Text contrast' or len(templists) >= 3 and templists[0] == 'Image contrast':

                                            issuecolor = get_color_issueInfo(templists[2])
                                            # print("123")
                                            if templists[1].find(":id") != -1:
                                                id_set = templists[1].split(":id/")
                                                # print(f'id_set : {id_set}')
                                                if len(id_set) > 1:
                                                    id = id_set[1]
                                                    # print(id)
                                                text_values = get_text_by_id(id, nodes_info)
                                                # print(id)
                                                # print('**********')
                                                # print(text_values)
                                                if text_values:
                                                    # print(text_values)
                                                    id_or_bound_list[(id,text_values)] = issuecolor
                                                    id_or_bound_class_list[(id,text_values)] = (issuecolor,templists[0])
                                                else:
                                                    id_or_bound_list[(id,'')] = issuecolor
                                                    id_or_bound_class_list[(id,'')] = (issuecolor, templists[0])
                                                # id_or_bound_list[id] = issuecolor
                                                # id_or_bound_class_list[id] = (issuecolor,templists[0])

                                            else:

                                                # if templists[1] in bounds_dict:
                                                #     print(templists[1])
                                                if templists[1].startswith("[") and templists[1] in bounds_dict:

                                                    text_values = get_text_by_bound(templists[1],bounds_dict)

                                                    id_or_bound_list['',text_values[0]] = issuecolor
                                                    id_or_bound_class_list['',text_values[0]] = (issuecolor,templists[0])



                                        templists = []

    return id_or_bound_class_list


def parse_strings_xml(string_xml_path):
    strings_dict = {}
    if not os.path.exists(string_xml_path):
        return strings_dict
    try:
        tree = ET.parse(string_xml_path)
        root = tree.getroot()
        for string in root.findall('string'):
            name = string.get('name')
            text = string.text or ''
            strings_dict[text.strip().lower()] = name
    except ET.ParseError as e:
        print(f'Error : {e}')
    return strings_dict

def trans_text_to_string(component_with_issue,decomp_path):
    res_path = os.path.join(decomp_path,"res")
    values_path = os.path.join(res_path,"values")
    string_xml_path = os.path.join(values_path,"strings.xml")


    strings_dict = parse_strings_xml(string_xml_path)

    updated_component = {}


    for (id_value,text_value),value in component_with_issue.items():
        norm_text = text_value.strip().lower()

        if norm_text in strings_dict:
            new_text = strings_dict[norm_text]

            updated_component[(id_value,new_text)] = value
        else:
            updated_component[(id_value,text_value)] = value

    return updated_component


def find_nothing_issue(act_name,report_path):
    no_id_text_issue = []
    layout_path = os.path.join(report_path,"layouts")
    # print(layout_path)
    nodes_info,bounds_dict= get_all_bound(layout_path,act_name)
    # print(nodes_info)
    for file in os.listdir(report_path):

        if file.startswith('issue'):
            dir1_path = os.path.join(report_path,file)
            # print(dir1_path)
            for act in os.listdir(dir1_path):

                # print(act)
                if act == act_name:
                    # print(act)
                    act_path = os.path.join(dir1_path,act)
                    # print(act_path)
                    for txt_file in os.listdir(act_path):

                        # print(txt_file)
                        if txt_file.endswith(".txt"):
                            with open(os.path.join(act_path,txt_file),"r",encoding='utf-8') as f:
                                lis = []
                                lists = []
                                templists = []

                                for line in f:
                                    lis.append(line)

                                for li in lis:

                                    li = li.split("\n")
                                    lists.append(li[0])

                                for l in lists:
                                    if l != "":
                                        templists.append(l)

                                    else:
                                        '''
                                        Text contrast
                                        a2dp.Vol:id/pi_tv_name
                                        The item's text contrast ratio is 1.04. This ratio is based on an estimated foreground color of #FFFFFF and an estimated background color of #FAFAFA. Consider increasing this item's text contrast ratio to 3.00 or greater.
                                        '''
                                        if len(templists) >= 3 and templists[0] == 'Text contrast' or len(templists) >= 3 and templists[0] == 'Image contrast':

                                            if templists[1].startswith("[") and templists[1] in bounds_dict:
                                                text_values = get_text_by_bound(templists[1],bounds_dict)

                                                if text_values == '':
                                                    no_id_text_issue.append(templists[1])

                                        templists = []
    return no_id_text_issue





def get_id_inOneAPK(APK_Path, APKName, outputsPath):
    ids_inOneAPK = {}
    stringBound = {}
    stringBound_b = {}

    for file in os.listdir(APK_Path):

        if file.endswith(".txt"):

            with open(os.path.join(APK_Path, file), "r") as f:
                lis = []
                lists = []
                tempLists = []

                for line in f:
                    lis.append(line)


                for li in lis:
                    li = li.split("\n")
                    lists.append(li[0])

                id_or_bounds_List = {}


                for l in lists:
                    if l != "":
                        tempLists.append(l)

                    else:

                        '''
                        Text contrast
                        a2dp.Vol:id/pi_tv_name
                        The item's text contrast ratio is 1.04. This ratio is based on an estimated foreground color of #FFFFFF and an estimated background color of #FAFAFA. Consider increasing this item's text contrast ratio to 3.00 or greater.
                        '''
                        if tempLists[1].find(":id/") != -1:

                            id = tempLists[1].split(":id/")

                            issueColor = get_results.get_color_issueInfo(tempLists[2])


                            id_or_bounds_List[id[1]] = issueColor

                            ids_inOneAPK[id[1]] = (issueColor, tempLists[0])

                        else:
                            issueColor = get_results.get_color_issueInfo(tempLists[2])

                            if tempLists[1].startswith("[") and tempLists[1] in bound_text:


                                id_or_bounds_List[bound_text[tempLists[1]]] = issueColor

                                stringBound[bound_text[tempLists[1]]] = tempLists[1]
                                stringBound_b[bound_text[tempLists[1]][0]] = tempLists[1]
                                ids_inOneAPK[bound_text[tempLists[1]][0]] = (issueColor, colorRatio, file.split('.')[len(file.split('.')) - 2], bound_text[tempLists[1]][1], tempLists[0])
                            else:
                                id_or_bounds_List[tempLists[1]] = issueColor
                                ids_inOneAPK[tempLists[1]] = (issueColor, colorRatio, file.split('.')[len(file.split('.')) - 2], '', tempLists[0])
                        tempLists = []


    return ids_inOneAPK, stringBound, stringBound_b