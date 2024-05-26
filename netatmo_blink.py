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
    {"value": -22, "color": [ 29,  70, 154]},
    {"value": -16, "color": [ 20,  98, 169]},
    {"value": -11, "color": [ 22, 116, 182]},
    {"value":  -6, "color": [ 54, 138, 199]},
    {"value":  -3, "color": [ 63, 163, 218]},
    {"value":   0, "color": [ 78, 192, 238]},
    {"value":   1, "color": [174, 220, 216]},
    {"value":   3, "color": [168, 214, 173]},
    {"value":   5, "color": [158, 208, 127]},
    {"value":   7, "color": [174, 211,  82]},
    {"value":   9, "color": [208, 217,  62]},
    {"value":  11, "color": [252, 222,   4]},
    {"value":  13, "color": [251, 203,  12]},
    {"value":  15, "color": [252, 183,  22]},
    {"value":  17, "color": [250, 163,  26]},
    {"value":  19, "color": [246, 138,  31]},
    {"value":  21, "color": [242, 106,  47]},
    {"value":  25, "color": [236,  81,  57]},
    {"value":  30, "color": [237,  42,  42]},
    {"value":  36, "color": [195,  32,  39]},
    {"value":  41, "color": [155,  27,  29]}
]

# Pressure scale from 850 to 1050, using the
# same colours as the temperature scale
PRESSURE_SCALE = [
    {"value":  900.0, "color": [ 29,  70, 154]},
    {"value":  907.5, "color": [ 20,  98, 169]},
    {"value":  915.0, "color": [ 22, 116, 182]},
    {"value":  922.5, "color": [ 54, 138, 199]},
    {"value":  930.0, "color": [ 63, 163, 218]},
    {"value":  937.5, "color": [ 78, 192, 238]},
    {"value":  945.0, "color": [174, 220, 216]},
    {"value":  952.5, "color": [168, 214, 173]},
    {"value":  960.0, "color": [158, 208, 127]},
    {"value":  967.5, "color": [174, 211,  82]},
    {"value":  975.0, "color": [208, 217,  62]},
    {"value":  982.5, "color": [252, 222,   4]},
    {"value":  990.0, "color": [251, 203,  12]},
    {"value":  997.5, "color": [252, 183,  22]},
    {"value": 1005.0, "color": [250, 163,  26]},
    {"value": 1012.5, "color": [246, 138,  31]},
    {"value": 1020.0, "color": [242, 106,  47]},
    {"value": 1027.5, "color": [236,  81,  57]},
    {"value": 1035.0, "color": [237,  42,  42]},
    {"value": 1042.5, "color": [195,  32,  39]},
    {"value": 1050.0, "color": [155,  27,  29]}
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

        temperature = float(weather_data.lastData()[config['temp_room']]['Temperature'])
        pressure = float(weather_data.lastData()[config['pressure_room']]['Pressure'])

        if config['debug']:
            print(f'{temperature}, {pressure}')
            
        set_color(blink, temperature, pressure)

        time.sleep(int(config['update_interval']))
