import math
import random
import colorsys
from colorsys import rgb_to_hls, hls_to_rgb

def hex_to_rgb(hex_color):
    if not hex_color:
        raise ValueError("Invalid color: None provided")
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid color format: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_linear(rgb):

    return [((c / 255.0) / 12.92) if (c / 255.0) <= 0.03928 else ((c / 255.0 + 0.055) / 1.055) ** 2.4 for c in rgb]


def rgb_to_hsl(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s, l

def relative_luminance(rgb):

    linear_rgb = rgb_to_linear(rgb)
    return 0.2126 * linear_rgb[0] + 0.7152 * linear_rgb[1] + 0.0722 * linear_rgb[2]

def contrast_ratio(color1, color2):
    def get_luminance(c):
        if isinstance(c, str):
            c = hex_to_rgb(c)
        r, g, b = [x / 255.0 for x in c]
        # Apply gamma correction (sRGB → Linear RGB)
        r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1, l2 = get_luminance(color1), get_luminance(color2)
    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)


def adjust_brightness(rgb, factor):

    r, g, b = [x / 255.0 for x in rgb]

    h, l, s = rgb_to_hls(r, g, b)

    l = max(0, min(1, l * factor))

    new_r, new_g, new_b = hls_to_rgb(h, l, s)

    return '#{:02x}{:02x}{:02x}'.format(int(new_r * 255), int(new_g * 255), int(new_b * 255))


def find_brightness_adjustment(colors_set, color1, color2, target_ratio=4.5, max_iteration=1000000, adjustment_factor=1.01):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)


    current_ratio = contrast_ratio(color1, color2)

    if current_ratio >= target_ratio:
        return color1


    brighter_16 = adjust_brightness(rgb1, adjustment_factor)
    darker_16 = adjust_brightness(rgb1, 1 / adjustment_factor)

    brighter_ratio = contrast_ratio(brighter_16, color2)
    darker_ratio = contrast_ratio(darker_16, color2)

    if brighter_ratio > darker_ratio:
        adjustment_direction = adjustment_factor
    else:
        adjustment_direction = 1 / adjustment_factor

    res_color = rgb1
    for _ in range(max_iteration):
        res_color = adjust_brightness(res_color, adjustment_direction)
        adjusted_color = res_color
        res_color = hex_to_rgb(res_color)

        new_ratio = contrast_ratio(adjusted_color, color2)


        if new_ratio > target_ratio:

            return adjusted_color

    return color1

def luminance(c):

    if isinstance(c, str):
        c = hex_to_rgb(c)
    r, g, b = [x / 255.0 for x in c]
    r = r ** 2.2 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = g ** 2.2 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = b ** 2.2 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def generate_random_colors(background_color,target_ratio = 4.5,num_colors = 10):

    bg_lum = luminance(background_color)


    if bg_lum > 0.18:
        max_lum = (bg_lum + 0.05) / target_ratio - 0.05
        hsv_ranges = {
            'hue': (0, 1),
            'sat': (0.7, 1.0),
            'val': (0.05, max(0.05, max_lum))
        }
    else:
        min_lum = (bg_lum + 0.05) * target_ratio - 0.05
        hsv_ranges = {
            'hue': (0, 1),
            'sat': (0.7, 1.0),
            'val': (min(0.95, min_lum), 0.95)
        }

    colors = []
    while len(colors) < num_colors:

        hue = random.uniform(*hsv_ranges['hue'])
        sat = random.uniform(*hsv_ranges['sat'])
        val = random.uniform(*hsv_ranges['val'])


        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255),
            int(g * 255),
            int(b * 255)
        )

        if contrast_ratio(hex_color, background_color) >= target_ratio:
            colors.append(hex_color)

    return colors




def color_difference(color1,color2):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    return sum((c1 - c2) ** 2 for c1,c2 in zip(rgb1,rgb2)) ** 0.5



def hue_harmony(color1, color2):

    h1, s1, v1 = colorsys.rgb_to_hsv(color1[0]/255, color1[1]/255, color1[2]/255)
    h2, s2, v2 = colorsys.rgb_to_hsv(color2[0]/255, color2[1]/255, color2[2]/255)
    h1, h2 = h1 * 360, h2 * 360

    hue_diff = abs(h1 - h2)
    hue_diff = min(hue_diff, 360 - hue_diff)


    value_diff = abs(v1 - v2)


    if value_diff > 0.5:
        harmony_reduction = 0.5
    else:
        harmony_reduction = 1.0

    if hue_diff <= 15:
        base_harmony  =  20
    elif hue_diff <= 30:
        base_harmony  =  16
    elif hue_diff <= 90:
        base_harmony  =  10
    elif hue_diff <= 180:
        base_harmony  =  5
    else:
        base_harmony  =  2

    s = 1
    if abs(s1 - s2) > 0.3:
        s = 0.5

    final_harmony = int(base_harmony * harmony_reduction * s)
    return max(1, final_harmony)



def contrast_score(ratio):
    if ratio > 17:
        return 4
    elif ratio > 13:
        return 6
    elif ratio > 9:
        return 7
    elif ratio > 4.5:
        return 8
    else:
        return 10


def luminance_balance(color1, color2):
    _, _, l1 = rgb_to_hsl(*color1)
    _, _, l2 = rgb_to_hsl(*color2)
    lum_diff = abs(l1 - l2)
    if lum_diff <= 0.1:
        return 10
    elif lum_diff <= 0.3:
        return 8
    elif lum_diff <= 0.5:
        return 5
    else:
        return 2


def aesthetic_score(hex_color1, hex_color2):
    if hex_color1 is None or hex_color2 is None:
        raise ValueError(f"Invalid input: hex_color1 = {hex_color1}, hex_color2 = {hex_color2}")


    color1 = hex_to_rgb(hex_color1)
    color2 = hex_to_rgb(hex_color2)
    w1, w2, w3 = 1, 1, 1
    harmony = hue_harmony(color1, color2)
    contrast = contrast_score(contrast_ratio(color1, color2))
    luminance = luminance_balance(color1, color2)

    score = harmony
    return round(score, 2)


def find_most_candidate(candidates,color_set):
    best_color = None
    best_score = 0

    for candidate in candidates:
        candidate_score = 0
        for color in color_set:

            candidate_score += aesthetic_score(candidate,color[0]) * color[1]

        if candidate_score > best_score:
            best_color = candidate
            best_score = candidate_score

    return best_color

def last_method(back_color,colors_set):
    candidates = generate_random_colors(back_color, target_ratio=4.5, num_colors=10)
    last_color = find_most_candidate(candidates, colors_set)
    return last_color