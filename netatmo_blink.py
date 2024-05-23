from blink1.blink1 import blink1
import time
import lnetatmo
import toml

UPDATE_INTERVAL = 900
DEBUG = True
PRESSURE_ROOM = 'Living Room'

# Temperature colours from BBC Weather
# https://www.bbc.com/weather/features/66293839
TEMP_SCALE = [
    {"value": -22, "color": [29, 71, 152]},
    {"value": -16, "color": [20, 98, 167]},
    {"value": -11, "color": [20, 117, 180]},
    {"value":  -6, "color": [54, 138, 199]},
    {"value":  -3, "color": [63, 163, 218]},
    {"value":   0, "color": [80, 191, 236]},
    {"value":   1, "color": [174, 221, 214]},
    {"value":   3, "color": [168, 213, 175]},
    {"value":   5, "color": [168, 213, 175]},
    {"value":   7, "color": [174, 211, 82]},
    {"value":   9, "color": [208, 217, 62]},
    {"value":  11, "color": [254, 221, 4]},
    {"value":  13, "color": [253, 201, 16]},
    {"value":  15, "color": [253, 201, 16]},
    {"value":  17, "color": [250, 163, 28]},
    {"value":  19, "color": [246, 139, 29]},
    {"value":  21, "color": [246, 139, 29]},
    {"value":  25, "color": [239, 79, 58]},
    {"value":  30, "color": [237, 42, 40]},
    {"value":  36, "color": [237, 42, 40]},
    {"value":  41, "color": [156, 26, 29]}
]

# Pressure scale from 850 to 1050, using the
# same colours as the temperature scale
PRESSURE_SCALE = [
    {"value":  850, "color": [29, 71, 152]},
    {"value":  860, "color": [20, 98, 167]},
    {"value":  870, "color": [20, 117, 180]},
    {"value":  880, "color": [54, 138, 199]},
    {"value":  890, "color": [63, 163, 218]},
    {"value":  900, "color": [80, 191, 236]},
    {"value":  910, "color": [174, 221, 214]},
    {"value":  920, "color": [168, 213, 175]},
    {"value":  930, "color": [168, 213, 175]},
    {"value":  940, "color": [174, 211, 82]},
    {"value":  950, "color": [208, 217, 62]},
    {"value":  960, "color": [254, 221, 4]},
    {"value":  970, "color": [253, 201, 16]},
    {"value":  980, "color": [253, 201, 16]},
    {"value":  990, "color": [250, 163, 28]},
    {"value": 1000, "color": [246, 139, 29]},
    {"value": 1010, "color": [246, 139, 29]},
    {"value": 1020, "color": [239, 79, 58]},
    {"value": 1030, "color": [237, 42, 40]},
    {"value": 1040, "color": [237, 42, 40]},
    {"value": 1050, "color": [156, 26, 29]}
]

def _interpolate_color(color1, color2, proportion):
  return round(color1 + (color2 - color1) * proportion)

def get_rgb(value, scale):

    if value <= scale[0]['value']:
        result = scale[0]['color']
    elif value >= scale[-1]['value']:
        result = scale[-1]['color']
    else:
        prev_entry = scale[0]
        next_entry = scale[1]

        for i in range(0, len(scale)):
            if scale[i]["value"] == value:
                prev_entry = scale[i]
                next_entry = scale[i]
            elif scale[i]["value"] < value and scale[i + 1]["value"] > value:
                prev_entry = scale[i]
                next_entry = scale[i + 1]

        if prev_entry["color"] == next_entry["color"]:
            result = prev_entry["color"]
        else:
            color_proportion = (value - prev_entry["value"]) / (next_entry["value"] - prev_entry["value"])
            red_value = _interpolate_color(prev_entry["color"][0], next_entry["color"][0], color_proportion)
            green_value = _interpolate_color(prev_entry["color"][1], next_entry["color"][1], color_proportion)
            blue_value = _interpolate_color(prev_entry["color"][2], next_entry["color"][2], color_proportion)

            result = [red_value, green_value, blue_value]

    return result


def set_color(blink, temp, pressure):
    temp_rgb = get_rgb(temp, TEMP_SCALE)
    pressure_rgb = get_rgb(pressure, PRESSURE_SCALE)
    
    blink.fade_to_rgb(1000, temp_rgb[0], temp_rgb[1], temp_rgb[2], 1)
    blink.fade_to_rgb(1000, pressure_rgb[0], pressure_rgb[1], pressure_rgb[2], 2)



with open('config.toml') as c:
    config = toml.load(c)

with blink1() as blink:
    while True:
        authorization = lnetatmo.ClientAuth()
        weather_data = lnetatmo.WeatherStationData(authorization)

        temperature = weather_data.lastData()[config['temp_room']]['Temperature']
        pressure = weather_data.lastData()[config['pressure_room']]['Pressure']

        if config['debug']:
            print(f'{temperature}, {pressure}')
            
        set_color(blink, temperature, pressure)

        time.sleep(int(config['update_interval']))
