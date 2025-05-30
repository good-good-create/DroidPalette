# -*- coding: UTF8 -*-
import os


def getClickableID(APKName, report_Path):
    clickableIds = []


    clickableIdsInAct = {}


    layoutsPath = os.path.join(report_Path, APKName, "layouts")


    for actFullName in os.listdir(layoutsPath):
        if not actFullName.endswith('.xml'):
            continue

        act = actFullName.split('.')[-2]

        if act not in clickableIdsInAct:
            clickableIdsInAct[act] = []


        layout_path = os.path.join(layoutsPath, actFullName)
        with open(layout_path, "r") as f:
            con = f.read()

            for node in con.split('<node '):

                if (node.find('clickable="true"') != -1 and node.find('enabled="true"') != -1 and node.find('resource-id="') != -1) or (
                        node.find('long-clickable="true"') != -1 and node.find('enabled="true"') != -1 and node.find('resource-id="') != -1):
                    if node.find('esource-id=""') != -1:
                        continue


                    if node.split('resource-id="')[1].split('"')[0].find(':id/') != -1:
                        IdName = node.split('resource-id="')[1].split(':id/')[1].split('"')[0]
                    else:
                        IdName = node.split('resource-id="')[1].split('"')[0]

                    clickableIds.append(IdName)

                    if IdName not in clickableIdsInAct[act]:
                        clickableIdsInAct[act].append(IdName)

    return list(set(clickableIds)), clickableIdsInAct



