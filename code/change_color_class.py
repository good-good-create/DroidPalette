# encoding: utf-8
import os
from colorsys import rgb_to_hsv
from tkinter import Image

import cv2

import get_results
import nonIssueColorSet
import get_color_set
import colorSet_reference
import check_color
import changeImageCondition
import changeImageColor

import harmonizationTs2
import hsvRGB2
import get_clickableID2
import find_colors_set



def to_hsv(color):
    return rgb_to_hsv(*[x/255.0 for x in color])

def color_dist(c1, c2):
    return sum((a-b)**2 for a, b in zip(to_hsv(c1), to_hsv(c2)))

def min_color_diff( color_to_match, colorList):
    return min((color_dist(color_to_match, get_color_set.colorToRGB(test)), test)for test in colorList)

def sub(num1,num2):
    if num1 > num2:
        return num1 - num2
    else:
        return num2 - num1

def ratioNum(txt):
    if txt.find("greater than 4.50 for small text") != -1:
        colorRatio = 4.5
    else:
        colorRatio = 3
    return colorRatio

def get_bounds(txt):
    bound = (txt.split("bounds=\"")[1]).split("\"")[0]
    return bound

def get_text(txt):

    if txt.find("text=\"") == -1:
        return ""

    if txt.find("text=\"@string/") != -1:
        text = (txt.split("text=\"@string/")[1]).split("\"")[0]
    else:

        text = (txt.split("text=\"")[1]).split("\"")[0]
    return text

def get_textCmponent(txt):
    if txt.find("class=\"") == -1:
        return ""
    compon = (txt.split("class=\"")[1]).split("\"")[0]
    return compon.split(".")[len(compon.split(".")) - 1]




def get_id_inOneAPK(APK_Path, APKName, outputsPath):
    null_id = []
    act_ids = {}
    ids_inOneAPK = {}
    stringBound = {}
    stringBound_b = {}
    activity = []
    for file in os.listdir(APK_Path):

        if file.endswith(".txt"):
            img = ''
            imgTag = 0
            fileT = file

            bound_text, bound_id = find_text_for_location(APKName, fileT.split(".xml")[0], outputsPath)

            pngFile = os.path.join(outputsPath, APKName, "screenshot", fileT.split(".txt")[0])
            if os.path.exists(pngFile):
                for fi in os.listdir(pngFile):

                    if fi.endswith(".png") and not fi.endswith("_thumbnail.png"):

                        img_path = os.path.join(pngFile, fi)
                        img = cv2.imread(img_path)
                        if img is not None:
                            img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

                            pil_img = Image.fromarray(img_rgb)

                            candi_color = find_colors_set.extract_colors(pil_img)


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

                            if id[1] in bound_id:

                                stringBound[(id[1], bound_id[id[1]][1])] = bound_id[id[1]][0]
                            else:

                                null_id.append(id[1])

                            if issueColor[1] == issueColor[0] or tempLists[1].find('android:id/') != -1:

                                null_id.append(id[1])


                            if imgTag == 1 and id[1] in bound_id and check_color.checkColorSet(img, issueColor, bound_id[id[1]][0]) == 0:
                                print ( id[1] )
                                issueColor1 = issueColor
                                issueColor = [issueColor1[1], issueColor1[0]]


                            colorRatio = ratioNum(tempLists[2])

                            id_or_bounds_List[id[1]] = issueColor

                            ids_inOneAPK[id[1]] = (issueColor, colorRatio, file.split('.')[len(file.split('.')) - 2], '', tempLists[0])

                            activity.append(file.split('.')[len(file.split('.')) - 2])

                        else:
                            issueColor = get_results.get_color_issueInfo(tempLists[2])
                            colorRatio = ratioNum(tempLists[2])

                            if tempLists[1].startswith("[") and tempLists[1] in bound_text:


                                if tempLists[1] in bound_text and check_color.checkColorSet(img, issueColor, tempLists[1]) == 0:
                                    issueColor1 = issueColor
                                    issueColor = [issueColor1[1], issueColor1[0]]

                                if bound_text[tempLists[1]][0] == '' or bound_text[tempLists[1]][0].isspace() or issueColor[1] == issueColor[0]:
                                    null_id.append(tempLists[1])


                                id_or_bounds_List[bound_text[tempLists[1]]] = issueColor


                                stringBound[bound_text[tempLists[1]]] = tempLists[1]


                                stringBound_b[bound_text[tempLists[1]][0]] = tempLists[1]

                                ids_inOneAPK[bound_text[tempLists[1]][0]] = (issueColor, colorRatio, file.split('.')[len(file.split('.')) - 2], bound_text[tempLists[1]][1], tempLists[0])
                                activity.append(file.split('.')[len(file.split('.')) - 2])

                            else:

                                id_or_bounds_List[tempLists[1]] = issueColor
                                ids_inOneAPK[tempLists[1]] = (issueColor, colorRatio, file.split('.')[len(file.split('.')) - 2], '', tempLists[0])
                                activity.append(file.split('.')[len(file.split('.')) - 2])
                        tempLists = []

                act_ids[file.split(".txt")[0]] = id_or_bounds_List

    return act_ids, ids_inOneAPK, list(set(activity)), list(set(null_id)), stringBound, stringBound_b


def get_id_txt(txt):
    id = ''
    if txt.find("android:id=\"@id/") != -1:
        id = (txt.split("android:id=\"@id/")[1]).split("\"")[0]
    elif txt.find("android:id=\"@+id/") != -1:
        id = (txt.split("android:id=\"@+id/")[1]).split("\"")[0]
    elif txt.find("android:id=\"@android:id/") != -1:
        id = (txt.split("android:id=\"@android:id/")[1]).split("\"")[0]
    elif txt.find(":id=\"@id/") != -1:
        id = (txt.split(":id=\"@id/")[1]).split("\"")[0]
    elif txt.find(":id=\"@android:id/") != -1:
        id = (txt.split(":id=\"@android:id/")[1]).split("\"")[0]
    return id

def get_text_txt(txt):
    text =''
    if txt.find(":text=\"") != -1:
        text = (txt.split(":text=\"")[1]).split("\"")[0]
    elif txt.find(":text=\"@string/") != -1:
        text = (txt.split(":text=\"@string/")[1]).split("\"")[0]
    elif txt.find(":title=\"@string/") != -1:
        text = (txt.split(":title=\"@string/")[1]).split("\"")[0]
    elif txt.find(":title=\"") != -1:
        text = (txt.split(":title=\"")[1]).split("\"")[0]
    return text

def get_title_txt(txt):
    title =''
    if txt.find(":title=\"") != -1:
        title = (txt.split(":title=\"")[1]).split("\"")[0]
    return title

def get_style_txt(txt):
    # android:textAppearance="@style/TextAppearance.AppCompat.Medium"
    style = ""
    if txt.find("=\"@style/") != -1:
        style = (txt.split("=\"@style/")[1]).split("\"")[0]
    return style

def get_color_styleTxt(txt):
    if txt.find("android:textColor") != -1:
        color = (txt.split("name=\"android:textColor\">")[1]).split("</item>")[0]
    return color

def get_stringText(txt):
    return (txt.split(">")[1]).split("</string")[0]

def get_componentClass(txt):
    class_list = ["Button", "TextView", "ImageView", "ImageButton", "EditText"]
    componentClass = txt.split(" ")[0]
    if componentClass in class_list:
        return componentClass
    else:
        return "TextView"

def get_Tag(txt):
    for t in txt.split(' '):
        if t.find(':id="') != -1:
            tagT = t.split(':id="')[0]
            break
        elif t.find(':text="') != -1:
            tagT = t.split(':text="')[0]
            break
    return tagT


def findInString(decom_Path, ids_inOneAPK):
    bounds_inOneAPK = {}
    stringText = {}
    for file in os.listdir(os.path.join(decom_Path, "res")):
        if not file.startswith("values"):
            continue
        if "strings.xml" in os.listdir(os.path.join(decom_Path, "res", file)):
            f = open(os.path.join(decom_Path, "res", file, "strings.xml"), "r")
            allTXT = f.read()
            allTXT = allTXT.split("<string ")
            for txt in allTXT:
                if not txt.startswith("name"):
                    continue

                if get_stringText(txt) in ids_inOneAPK or get_stringText(txt) in stringText:

                    stringName = (txt.split("name=\"")[1]).split("\"")[0]
                    if get_stringText(txt) in stringText:
                        bounds_inOneAPK[(txt.split("name=\"")[1]).split("\"")[0]] = bounds_inOneAPK[stringText[get_stringText(txt)]]

                    else:
                        stringText[get_stringText(txt)] = stringName
                        bounds_inOneAPK[stringName] = ids_inOneAPK[get_stringText(txt)]
                        del ids_inOneAPK[get_stringText(txt)]

    ids_bounds_inOneAPK = dict(list(ids_inOneAPK.items()) + list(bounds_inOneAPK.items()))
    return ids_bounds_inOneAPK, ids_inOneAPK, bounds_inOneAPK, stringText

def solveTextContrast(decom_Path, id, txt, colorToChange, colorName_colorNew, id_style, nonIssueColorAct, id_bound_colorSet, colorToChange_class, act_T_Alpha):

    componentClass = get_componentClass(txt)
    drawableNames = []
    text_color = ''
    # if componentClass == 'Button':
    if 1 == -1:
        # print id
        # print txt
        if txt.find(":textColor=\"") != -1 or txt.find(":textColorLink=\"") != -1 or txt.find(":titleTextColor=\"") != -1:
            # print txt
            txt_temp1 = txt
            if txt.find(":textColor=\"") != -1:
                text_color = (txt_temp1.split(":textColor=\"")[1]).split("\"")[0]
                # print old_color
            if txt.find(":textColorLink=\"") != -1:
                text_color = (txt_temp1.split(":textColorLink=\"")[1]).split("\"")[0]
            elif txt.find(":titleTextColor=\"") != -1:
                text_color = (txt_temp1.split(":titleTextColor=\"")[1]).split("\"")[0]
        if txt.find(":background=\"@drawable/") != -1:
            txt_temp1 = txt
            drawableName = (txt_temp1.split(":background=\"@drawable/")[1]).split("\"")[0]
            # print drawableName
            for drawablesFloder in os.listdir(os.path.join(decom_Path, "res")):
                if not drawablesFloder.startswith("drawable"):
                    continue
                # print drawablesFloder
                drawablePath = os.path.join(decom_Path, "res", drawablesFloder)
                if drawableName + '.png' in os.listdir(drawablePath):
                    # print drawableName
                    drawableNamePath = os.path.join(drawablePath, drawableName + '.png')
                    drawableNames.append(drawableNamePath)
        # print drawableNames
        # print text_color
        tagC = 0

        if drawableNames != [] and text_color != '':
            drawableNameColor = changeImageCondition.colorToRGB(changeImageCondition.imageCondition1(drawableNames[0])[1][0][1])
            # print drawableNameColor
            [color0, color1] = id_bound_colorSet[id][0]
            # print color0, color1
            text_color6 = ''
            if len(text_color) == 9:
                # print text_color
                text_color6 = '#' + text_color[3:].upper()
                # print text_color
            # print check_color.checkColor(drawableNameColor, color1)
            # print  check_color.checkColor(text_color, color0)
            if text_color.startswith('#') and check_color.checkColor(drawableNameColor, color1) == 1 and check_color.checkColor(text_color6, color0) != 1:
                if id not in colorToChange:
                    colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, componentClass, id, colorToChange_class, act_T_Alpha)
                    # print colorToChange
                    colorToChange[id] = colorToC[id]
                imageChageC = colorToChange[id]
                if get_color_set.con_contrast(text_color6, imageChageC) >= 4.5:
                    textChageC = text_color6
                elif get_color_set.con_contrast("#000000", imageChageC) >= 4.5:
                    textChageC = "#000000"
                elif get_color_set.con_contrast("#FFFFFF", imageChageC) >= 4.5:
                    textChageC = "#FFFFFF"

                for d in drawableNames:
                    # print "hhh"
                    # print d
                    img = changeImageColor.transparence2white(d, imageChageC)
                    cv2.imwrite(d, img)
                txt = txt.replace(text_color, textChageC)
                tagC = 1
                # print textChageC
                # print imageChageC

        if text_color != '' and tagC == 0:
            # print id
            if id not in colorToChange:
                colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, componentClass, id,
                                              colorToChange_class, act_T_Alpha)
                # print colorToChange
                colorToChange[id] = colorToC[id]
            # print text_color
            # print colorToChange[id]
            txt = txt.replace(text_color, colorToChange[id])
            # print txt

        elif txt.find("@style/") != -1:
            id_style[get_style_txt(txt)] = (id, componentClass)
        else:
            if id not in colorToChange:
                colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, componentClass, id, colorToChange_class, act_T_Alpha)
                colorToChange[id] = colorToC[id]

            if txt.find("android:id=") != -1:
                txt = txt.split("android:id=")[0] + "android:textColor=\"" + colorToChange[
                    id] + "\" " + "android:id=" + txt.split("android:id=")[1]
            elif txt.find("android:text=") != -1:
                txt = txt.split("android:text=")[0] + "android:textColor=\"" + \
                           colorToChange[id] + "\" " + "android:text=" + txt.split("android:text=")[1]
            else:
                tagT = get_Tag(txt)
                # print tagT
                txt = txt.split(id + '"')[0] + id + '" ' + tagT + ":textColor=\"" + \
                           colorToChange[id] + "\"" + \
                           txt.split(id + '"')[1]

    else:
        if txt.find(":textColor=\"") != -1 or txt.find(":textColorLink=\"") != -1 or txt.find(":titleTextColor=\"") != -1:
            # print txt
            txt_temp1 = txt
            if txt.find(":textColor=\"") != -1:
                old_color = (txt_temp1.split(":textColor=\"")[1]).split("\"")[0]
                # print old_color
            if txt.find(":textColorLink=\"") != -1:
                old_color = (txt_temp1.split(":textColorLink=\"")[1]).split("\"")[0]
            elif txt.find(":titleTextColor=\"") != -1:
                old_color = (txt_temp1.split(":titleTextColor=\"")[1]).split("\"")[0]

            if id in colorToChange:
                txt = txt.replace(old_color, colorToChange[id])
            else:
                # print id
                colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, componentClass, id, colorToChange_class, act_T_Alpha)
                # print colorToChange
                colorToChange[id] = colorToC[id]
                # print colorToChange
                txt = txt.replace(old_color, colorToChange[id])
            # print old_color
            if old_color.startswith('@color/'):
                colorName_colorNew[old_color.split('@color/')[1]] = colorToChange[id]
        elif txt.find("@style/") != -1:
            id_style[get_style_txt(txt)] = (id, componentClass)
        else:
            if id not in colorToChange:
                colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, componentClass, id, colorToChange_class, act_T_Alpha)
                colorToChange[id] = colorToC[id]

            if txt.find("android:id=") != -1:
                txt = txt.split("android:id=")[0] + "android:textColor=\"" + colorToChange[
                    id] + "\" " + "android:id=" + txt.split("android:id=")[1]
            elif txt.find("android:text=") != -1:
                txt = txt.split("android:text=")[0] + "android:textColor=\"" + \
                           colorToChange[id] + "\" " + "android:text=" + txt.split("android:text=")[1]
            else:
                tagT = get_Tag(txt)
                # print tagT
                txt = txt.split(id + '"')[0] + id + '" ' + tagT + ":textColor=\"" + \
                           colorToChange[id] + "\"" + \
                           txt.split(id + '"')[1]

    return txt, id_style, colorToChange

def solveImageContrast(id, txt, colorToChange, imageId_style, nonIssueColorAct, id_bound_colorSet, imageId_Name, id_class):
    # :tint =
    componentClass = ''
    if id_bound_colorSet[id][3] == '':
        componentClass = get_componentClass(txt)
    else:
        componentClass = id_bound_colorSet[id][3]
    id_class[id] = componentClass

    if txt.find(":src=\"@drawable/") != -1:
        txt_temp1 = txt
        drawableName = (txt_temp1.split(":src=\"@drawable/")[1]).split("\"")[0]
        if (id, componentClass) not in imageId_Name:
            imageId_Name[(id, componentClass)] = []
        if drawableName not in imageId_Name[(id, componentClass)]:
            imageId_Name[(id, componentClass)].append(drawableName)
    elif txt.find(":srcCompat=\"@drawable/") != -1:
        txt_temp1 = txt
        drawableName = (txt_temp1.split(":srcCompat=\"@drawable/")[1]).split("\"")[0]
        if (id, componentClass) not in imageId_Name:
            imageId_Name[(id, componentClass)] = []
        if drawableName not in imageId_Name[(id, componentClass)]:
            imageId_Name[(id, componentClass)].append(drawableName)
    elif txt.find(":background=\"@drawable/") != -1:
        txt_temp1 = txt
        drawableName = (txt_temp1.split(":background=\"@drawable/")[1]).split("\"")[0]
        if (id, componentClass) not in imageId_Name:
            imageId_Name[(id, componentClass)] = []
        if drawableName not in imageId_Name[(id, componentClass)]:
            imageId_Name[(id, componentClass)].append(drawableName)
    elif txt.find("@style/") != -1:
        imageId_style[get_style_txt(txt)] = (id, componentClass, id_bound_colorSet[id][0])

    return txt, colorToChange, imageId_Name, imageId_style, id_class


def changeLayout_decompileAPK(decom_Path, id_bound_colorSet, colorToChange, nonIssueColorAct, colorToChange_class, act_T_Alpha):
    imageId_Name = {}
    editId = []
    id_style = {}
    id_class = {}
    imageId_style = {}
    colorName_colorNew = {}
    for id in id_bound_colorSet:
        if id_bound_colorSet[id][3] == 'EditText':
            editId.append(id)
    for layoutFloder in os.listdir(os.path.join(decom_Path, "res")):
        if not layoutFloder.startswith("layout"):
            continue

        for xmlFile in os.listdir(os.path.join(decom_Path, "res", layoutFloder)):
            if xmlFile.endswith(".xml"):

                TXTFile = xmlFile.split(".xml")[0] + ".txt"

                os.rename(os.path.join(decom_Path, "res", layoutFloder, xmlFile),
                          os.path.join(decom_Path, "res", layoutFloder, TXTFile))

        for TXTFile in os.listdir(os.path.join(decom_Path, "res", layoutFloder)):
            allData = ""
            # print TXTFile
            if TXTFile.endswith(".txt"):
                f = open(os.path.join(decom_Path, "res", layoutFloder, TXTFile), "r")
                allTXT = f.read()

                allTXT = allTXT.split("<")
                for txt in allTXT:

                    if txt.find(":id=") == -1 and txt.find(":text=") == -1 and txt != "" and txt.find(":title=") == -1:
                        allData += "<" + txt
                        continue

                    elif (get_id_txt(txt) in id_bound_colorSet) or (get_text_txt(txt) in id_bound_colorSet) or (get_title_txt(txt) in id_bound_colorSet):
                        if (get_id_txt(txt) in id_bound_colorSet) and (get_id_txt(txt) not in editId):

                            id = get_id_txt(txt)
                        elif get_text_txt(txt) in id_bound_colorSet and (get_text_txt(txt) not in editId):
                            id = get_text_txt(txt)
                        elif get_title_txt(txt) in id_bound_colorSet and (get_title_txt(txt) not in editId):
                            id = get_title_txt(txt)


                        if txt.startswith("EditText") or txt0.split(' ')[0].find("EditText") != -1:
                            editId.append(get_id_txt(txt))
                            allData += "<" + txt
                            continue

                        elif id_bound_colorSet[id][4] == 'Text contrast':

                            solution = solveTextContrast(decom_Path, id, txt, colorToChange, colorName_colorNew, id_style,
                                                  nonIssueColorAct, id_bound_colorSet, colorToChange_class, act_T_Alpha)
                            txt = solution[0]
                            id_style = solution[1]
                            colorToChange = solution[2]
                            allData += "<" + txt

                        elif id_bound_colorSet[id][4] == 'Image contrast':
                            # print id
                            # print txt
                            solution = solveImageContrast(id, txt, colorToChange, imageId_style, nonIssueColorAct, id_bound_colorSet, imageId_Name, id_class)
                            txt = solution[0]

                            colorToChange = solution[1]
                            imageId_Name = solution[2]
                            imageId_style = solution[3]
                            id_class = solution[4]
                            allData += "<" + txt

                    elif txt != '':
                        allData += "<" + txt
                # print allData

            with open(os.path.join(decom_Path, "res", layoutFloder, TXTFile), 'a+') as test:
                test.truncate(0)

            with open(os.path.join(decom_Path, "res", layoutFloder, TXTFile), "w") as f:
                # print allData
                f.write(allData)

        for txtFile in os.listdir(os.path.join(decom_Path, "res", layoutFloder)):
            if txtFile.endswith(".txt"):
                xmlFile = txtFile.split(".txt")[0] + ".xml"
                os.rename(os.path.join(decom_Path, "res", layoutFloder, txtFile),
                          os.path.join(decom_Path, "res", layoutFloder, xmlFile))

    for id_componentClass in imageId_Name:
        id = id_componentClass[0]
        ##220301
        # if id not in colorToChange:
        #     colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, id_class[id], id, colorToChange_class, act_T_Alpha)
        #     colorToChange[id] = colorToC[id]
        colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, id_class[id], id, colorToChange_class, act_T_Alpha)
        imageId_Name[id_componentClass] = (imageId_Name[id_componentClass], colorToC)
    # print "imageId_Name"
    # print imageId_Name
    # print "imageId_style"
    # print imageId_style
    return list(set(editId)), colorToChange, id_style, colorName_colorNew, imageId_Name, imageId_style

def get_colorName(txt):
    return txt.split('@color/')[1]

def get_styleName(txt):
    return (txt.split("name=\"")[1]).split("\"")[0]

def changeStyle_decompileAPK(decom_Path, id_style, imageId_style, imageId_Name, id_bound_colorSet, colorToChange, nonIssueColorAct, colorName_colorNew, Manifest, colorToChange_class, act_T_Alpha):
    # colorName_colorNew = {}
    # if not os.path.exists(os.path.join(decom_Path, "res", "values")):
    styleXmlFile = "styles.xml"
    for valuesFloder in os.listdir(os.path.join(decom_Path, "res")):
        if not valuesFloder.startswith("values"):
            continue
        # print valuesFloder
        if styleXmlFile in os.listdir(os.path.join(decom_Path, "res", valuesFloder)):
            TXTFile = styleXmlFile.split(".xml")[0] + ".txt"
            os.rename(os.path.join(decom_Path, "res", valuesFloder, styleXmlFile),
                          os.path.join(decom_Path, "res", valuesFloder, TXTFile))

            allData = ""
            f = open(os.path.join(decom_Path, "res", valuesFloder, TXTFile), "r")
            allTXT = f.read()
            # print allTXT
            allTXT = allTXT.split("<style ")
            for txt in allTXT:
                # print txt
                if txt.startswith("name"):
                    if (get_styleName(txt) not in id_style) and (get_styleName(txt) not in imageId_style) and (get_styleName(txt) not in Manifest) and txt != '':
                        allData += "<style " + txt
                        continue
                    elif get_styleName(txt) in id_style:
                        if txt.find("android:textColor") == -1:
                            allData += "<style " + txt
                            continue
                        else:
                            txtT = txt
                            id_component = id_style[(txtT.split("name=\"")[1]).split("\"")[0]]
                            # print txt
                            colorNameT = get_color_styleTxt(txt)

                            if id_component[0] in colorToChange:
                                txt = txt.replace(colorNameT, colorToChange[id_component[0]])
                            else:
                                colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, id_component[1],
                                                              id_component[0], colorToChange_class, act_T_Alpha)
                                # print colorToChange[id_component[0]]
                                colorToChange[id_component[0]] = colorToC[id_component[0]]
                                txt = txt.replace(colorNameT, colorToC[id_component[0]])
                            # print txt
                            if colorNameT.find('@color/') != -1:
                                colorName = get_colorName(colorNameT)
                                colorName_colorNew[colorName] = colorToChange[id_component[0]]

                            allData += "<style " + txt
                    elif get_styleName(txt) in imageId_style:
                        # if txt.find("srcCompat") == -1 and txt.find('background') == -1 and txt.find("srcCompat") == -1 and txt != '':
                        if txt.find('@drawable/') == -1 and txt != '':
                            allData += "<style " + txt
                            continue
                        else:
                            txtT = txt
                            draName = (txtT.split('@drawable/')[1]).split('<')[0]
                            if draName not in imageId_Name[imageId_style[get_styleName(txt)][0]][0]:
                                id = imageId_style[get_styleName(txt)][0]
                                imageId_Name[(id, id_bound_colorSet[id][3])][0].append(draName)
                    elif get_styleName(txt) in Manifest:
                        # print get_styleName(txt)
                        txtT = txt
                        # id_style[get_style_txt(txt)] = (id, componentClass)
                        id_component = Manifest[(txtT.split("name=\"")[1]).split("\"")[0]]
                        if id_component[0] not in colorToChange:
                            colorToC = find_colorToChange(nonIssueColorAct, id_bound_colorSet, id_component[1],
                                                          id_component[0], colorToChange_class, act_T_Alpha)
                            # print colorToChange[id_component[0]]
                            colorToChange[id_component[0]] = colorToC[id_component[0]]
                        if txt.find('<item name=') != -1:
                            if txt.find('<item name="titleTextColor">') == -1:
                                txt0 = txt.split('</style>')
                                allData += '<style ' + txt0[0] + '\t' + '<item name="titleTextColor">' + colorToChange[
                                    id_component[0]] + '</item>' + '</style>' + '\n'
                            else:
                                txt0 = txt
                                colorNameT = (txt0.split('<item name="titleTextColor">')[1]).split('<')[0]
                                txt = txt.replace(colorNameT, colorToChange[id_component[0]])
                                allData += "<style " + txt
                        else:
                            txt = txt.split('/>')[0] + '>' + '\n\t' + '<item name="titleTextColor">' + colorToChange[
                                    id_component[0]] + '</item>' + '</style>' + '\n'
                            allData += "<style " + txt

                else:
                    allData += txt

            with open(os.path.join(decom_Path, "res", valuesFloder, TXTFile), 'a+') as test:
                test.truncate(0)
            with open(os.path.join(decom_Path, "res", valuesFloder, TXTFile), "w") as f:
                # print allData
                f.write(allData)

            xmlFile = TXTFile.split(".txt")[0] + ".xml"
            os.rename(os.path.join(decom_Path, "res", valuesFloder, TXTFile),
                              os.path.join(decom_Path, "res", valuesFloder, xmlFile))
    # print "imageId_Name2"
    # print imageId_Name
    return colorToChange, colorName_colorNew, imageId_Name

def get_AppLable(txt):
    if txt.find(':label="@string/') != -1:
        return (txt.split(':label="@string/')[1]).split('"')[0]
    elif txt.find(':label="') != -1:
        return (txt.split(':label="')[1]).split('"')[0]

def get_theme(txt):
    return (txt.split(':theme="@style/')[1]).split('"')[0]

def changeManifestF_decompileAPK(decom_Path, id_bound_colorSet, stringText):
    id_style_ManifestF = {}
    ManifestXmlFile = 'AndroidManifest.xml'
    if ManifestXmlFile in os.listdir(decom_Path):
        f = open(os.path.join(decom_Path, ManifestXmlFile), "r")
        allTXT = f.read()
        allTXT = allTXT.split("<")
        for txt in allTXT:

            if txt.find(':label=') != -1 and txt.find(':theme=') != -1:

                id = get_AppLable(txt)
                if id in id_bound_colorSet:
                    id_style_ManifestF[get_theme(txt)] = (id, 'TextView')
                elif id in stringText:
                    id_style_ManifestF[get_theme(txt)] = (stringText[id], 'TextView')

    return id_style_ManifestF

def changeImages_decompileAPK(decom_Path, id_bound_colorSet, imageId_NameF, clickableIds):
    imagesToChangeF, imageids = changeImageCondition.changeSourceImage(decom_Path, imageId_NameF, id_bound_colorSet, clickableIds)
    for imgPath in imagesToChangeF:
        print (imgPath)
        for idw in imagesToChangeF[imgPath]:
            img = changeImageColor.transparence2white(imgPath, imagesToChangeF[imgPath][idw])
        cv2.imwrite(imgPath, img)
    return imageids
