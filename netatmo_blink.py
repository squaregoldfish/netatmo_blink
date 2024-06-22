from blink1.blink1 import blink1
import time
import lnetatmo
import toml

UPDATE_INTERVAL = 900
DEBUG = True
PRESSURE_ROOM = 'Living Room'

# Colours from BBC Weather
# https://www.bbc.com/weather/features/66293839

# Scaled for records from Bergen, Norway
# and Ostend, Belgium
TEMP_SCALE = [
    {"value": -18.0, "color": [ 29,  70, 154]},
    {"value": -15.1, "color": [ 20,  98, 169]},
    {"value": -12.2, "color": [ 22, 116, 182]},
    {"value":  -9.3, "color": [ 54, 138, 199]},
    {"value":  -6.4, "color": [ 63, 163, 218]},
    {"value":  -3.5, "color": [ 78, 192, 238]},
    {"value":  -0.6, "color": [174, 220, 216]},
    {"value":   2.3, "color": [168, 214, 173]},
    {"value":   5.2, "color": [158, 208, 127]},
    {"value":   8.1, "color": [174, 211,  82]},
    {"value":  11.0, "color": [208, 217,  62]},
    {"value":  13.9, "color": [252, 222,   4]},
    {"value":  16.8, "color": [251, 203,  12]},
    {"value":  19.7, "color": [252, 183,  22]},
    {"value":  22.6, "color": [250, 163,  26]},
    {"value":  25.5, "color": [246, 138,  31]},
    {"value":  28.4, "color": [242, 106,  47]},
    {"value":  31.3, "color": [236,  81,  57]},
    {"value":  34.2, "color": [237,  42,  42]},
    {"value":  37.1, "color": [195,  32,  39]},
    {"value":  40.0, "color": [155,  27,  29]}
]

# Pressure scale from 850 to 1050, using the
# same colours as the temperature scale
PRESSURE_SCALE = [
    {"value":  950.0, "color": [ 29,  70, 154]},
    {"value":  954.5, "color": [ 20,  98, 169]},
    {"value":  959.0, "color": [ 22, 116, 182]},
    {"value":  963.5, "color": [ 54, 138, 199]},
    {"value":  968.0, "color": [ 63, 163, 218]},
    {"value":  972.5, "color": [ 78, 192, 238]},
    {"value":  977.0, "color": [174, 220, 216]},
    {"value":  981.5, "color": [168, 214, 173]},
    {"value":  986.0, "color": [158, 208, 127]},
    {"value":  990.5, "color": [174, 211,  82]},
    {"value":  995.0, "color": [208, 217,  62]},
    {"value":  999.5, "color": [252, 222,   4]},
    {"value": 1004.0, "color": [251, 203,  12]},
    {"value": 1008.5, "color": [252, 183,  22]},
    {"value": 1013.0, "color": [250, 163,  26]},
    {"value": 1017.5, "color": [246, 138,  31]},
    {"value": 1022.0, "color": [242, 106,  47]},
    {"value": 1026.5, "color": [236,  81,  57]},
    {"value": 1031.0, "color": [237,  42,  42]},
    {"value": 1035.5, "color": [195,  32,  39]},
    {"value": 1040.0, "color": [155,  27,  29]}
]


def _interpolate_color(color1, color2, proportion):
  return round(color1 + (color2 - color1) * proportion)

def get_color(value, scale, type):

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

        if prev_entry['color'] == next_entry['color']:
            result = prev_entry['color']
        else:
            color_proportion = (value - prev_entry["value"]) / (next_entry["value"] - prev_entry["value"])
            red_value = _interpolate_color(prev_entry['color'][0], next_entry['color'][0], color_proportion)
            green_value = _interpolate_color(prev_entry['color'][1], next_entry['color'][1], color_proportion)
            blue_value = _interpolate_color(prev_entry['color'][2], next_entry['color'][2], color_proportion)

            result = [red_value, green_value, blue_value]

    if type == 'hex':
        return f'#{to_hex(result[0])}{to_hex(result[1])}{to_hex(result[2])}'
    else:
        return result


def to_hex(decimal):
    result = hex(decimal).split('x')[-1]
    return f'0{result}' if len(result) == 1 else result


def set_color(blink, temp, pressure):
    temp_rgb = get_color(temp, TEMP_SCALE, 'rgb')
    pressure_rgb = get_color(pressure, PRESSURE_SCALE, 'rgb')
    
    blink.fade_to_rgb(1000, temp_rgb[0], temp_rgb[1], temp_rgb[2], 1)
    blink.fade_to_rgb(1000, pressure_rgb[0], pressure_rgb[1], pressure_rgb[2], 2)



with open('config.toml') as c:
    config = toml.load(c)

with blink1() as blink:

    print(get_color(13.9, TEMP_SCALE, 'hex'))

    exit()
    authorization = lnetatmo.ClientAuth()
    while True:
        try:
            weather_data = lnetatmo.WeatherStationData(authorization)

            temperature = float(weather_data.lastData()[config['temp_room']]['Temperature'])
            pressure = float(weather_data.lastData()[config['pressure_room']]['Pressure'])

            if config['debug']:
                print(f'{temperature}, {pressure}')
                
            set_color(blink, temperature, pressure)

            with open(config['temperature_output_file'], 'w') as out:
                temp_color = get_color(temperature, TEMP_SCALE, 'hex')
                out.write(f'{temperature}°C\n\n{temp_color}')

            with open(config['pressure_output_file'], 'w') as out:
                pressure_color = get_color(pressure, PRESSURE_SCALE, 'hex')
                out.write(f'{pressure}hPa\n\n{pressure_color}')

            if config['debug']:
                print(f'{temp_color}, {pressure_color}\n')


        except Exception as e:
            print(e)

        time.sleep(int(config['update_interval']))
