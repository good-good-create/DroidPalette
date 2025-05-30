import os.path

import cv2
from PIL import Image
from collections import Counter


import calculate_ratio
from zmq.backend import second


def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0],rgb[1],rgb[2])


def extract_colors(image_path):
    min_percentage = 0.001
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return []


    if image.size[0] * image.size[1] > 1000000:
        image = image.resize((300, 300))
    pixels = list(image.getdata())


    color_counter = Counter(pixels)


    total_pixels = sum(color_counter.values())
    color_percentage = [(color, count / total_pixels) for color, count in color_counter.items()]


    color_percentage = [(rgb_to_hex(color), percentage)
                       for color, percentage in color_percentage
                       if percentage >= min_percentage]


    total_percent = sum(percent for _, percent in color_percentage)
    if total_percent > 0:
        color_percentage = [(color, percentage / total_percent)
                           for color, percentage in color_percentage]


    sorted_colors = sorted(color_percentage, key=lambda x: x[1], reverse=True)


    return sorted_colors
def find_colors(act_name,report_path):
    screenshot_path = os.path.join(report_path,"screenshot")
    act_screenshot_path = os.path.join(screenshot_path,act_name)

    for file in os.listdir(act_screenshot_path):
        if file.endswith(".png") and not file.endswith("_thumbnail.png"):
            img_path = os.path.join(act_screenshot_path,file)
            sorted_colors = extract_colors(img_path)
            return sorted_colors
            # for color, percentage in sorted_colors:
            #     print(f"{color}: {percentage:.2%}")


def color_equal(color1, color2):

    return color1.lower() == color2.lower()

def modify_color(issuecolor,colors_set):
    flag = 0
    max_score = 0
    second_largest = 0
    res_color = "#ffffff"
    valid_colors = []
    candidate_color = []
    fore_color = issuecolor[0]
    back_color = issuecolor[1]

    colors_set = sorted(colors_set,key=lambda item:item[1],reverse=True)


    adjust_color = calculate_ratio.find_brightness_adjustment(colors_set, issuecolor[0], issuecolor[1], 4.5, 100, 1.01)

    for colors,percentage in colors_set:
        if calculate_ratio.contrast_ratio(colors,issuecolor[1]) > 4.5:

            temp_score = ( calculate_ratio.aesthetic_score(colors, fore_color) + calculate_ratio.aesthetic_score(
                colors, back_color) ) * percentage
            for color,per in colors_set:
                temp_score += calculate_ratio.aesthetic_score(colors,color) * per * percentage

            if temp_score > max_score:
                res_color = colors
                max_score = temp_score
            candidate_color.append((colors,percentage,temp_score))
            if flag == 0:
                flag = 1

            temp_score = 0
    if len(colors_set) >= 2:
        second_largest = colors_set[1][1]
    else:
        second_largest = colors_set[0][1] if colors_set else 0


    if flag == 1 and color_equal(adjust_color,fore_color) != True:
        for colors,percentage,temp_score in candidate_color:
            if temp_score > max_score:
                max_score = temp_score
                res_color = colors
        adjust_color_score = (calculate_ratio.aesthetic_score(adjust_color,fore_color) + calculate_ratio.aesthetic_score(adjust_color,back_color)) * second_largest
        for color,per in colors_set:
            adjust_color_score += calculate_ratio.aesthetic_score(adjust_color,color) * per * second_largest

        res_color_score = max_score

        if adjust_color_score >= res_color_score:
            valid_colors.append((issuecolor[0],adjust_color))
        else:
            valid_colors.append((issuecolor[0],res_color))

    if flag == 0 and color_equal(adjust_color,fore_color) != True:

        valid_colors.append((issuecolor[0],adjust_color))

    if flag == 1 and color_equal(adjust_color,fore_color):

        valid_colors.append((issuecolor[0],res_color))

    if flag == 0 and color_equal(adjust_color,fore_color):

        last_color = calculate_ratio.last_method(back_color,colors_set)
        valid_colors.append((issuecolor[0],last_color))

    print("valid_colors",valid_colors)
    return valid_colors




def find_replace_color(component_with_issue,colors_set):

    # print(f'component_with_issue : {component_with_issue}')
    for key,(issuecolor,templists) in list(component_with_issue.items()):

        modified_color = modify_color(issuecolor,colors_set)

        component_with_issue[key] = (issuecolor,templists,modified_color,0)

    return component_with_issue

def process_same_dict(component_with_issue):
    color_list_pairs = {}
    process_dict = {}

    for key,value in component_with_issue.items():
        color_list = value[0]
        color_pairs = value[2]

        if tuple(color_list) in color_list_pairs:
            new_color_pairs = color_list_pairs[tuple(color_list)]
            new_value = (value[0],value[1],new_color_pairs,value[3])
            process_dict[key] = new_value
        else:
            color_list_pairs[tuple(color_list)] = color_pairs
            process_dict[key] = value

    return process_dict