from blink1.blink1 import blink1
import time
import toml
import requests
import traceback

def calc_steps(min, max, steps):
    step_size = (max - min) / (steps - 1)
    return [min + i * step_size for i in range(steps)]

# Colours from BBC Weather
# https://www.bbc.com/weather/features/66293839

# Scaled for records from Bruges, Belgium

TEMP_VALUES = calc_steps(-4, 37, 21)
TEMP_SCALE = [
    {"value": TEMP_VALUES[0], "color": [ 29,  70, 154]},
    {"value": TEMP_VALUES[1], "color": [ 20,  98, 169]},
    {"value": TEMP_VALUES[2], "color": [ 22, 116, 182]},
    {"value": TEMP_VALUES[3], "color": [ 54, 138, 199]},
    {"value": TEMP_VALUES[4], "color": [ 63, 163, 218]},
    {"value": TEMP_VALUES[5], "color": [ 78, 192, 238]},
    {"value": TEMP_VALUES[6], "color": [174, 220, 216]},
    {"value": TEMP_VALUES[7], "color": [168, 214, 173]},
    {"value": TEMP_VALUES[8], "color": [158, 208, 127]},
    {"value": TEMP_VALUES[9], "color": [174, 211,  82]},
    {"value": TEMP_VALUES[10], "color": [208, 217,  62]},
    {"value": TEMP_VALUES[11], "color": [252, 222,   4]},
    {"value": TEMP_VALUES[12], "color": [251, 203,  12]},
    {"value": TEMP_VALUES[13], "color": [252, 183,  22]},
    {"value": TEMP_VALUES[14], "color": [250, 163,  26]},
    {"value": TEMP_VALUES[15], "color": [246, 138,  31]},
    {"value": TEMP_VALUES[16], "color": [242, 106,  47]},
    {"value": TEMP_VALUES[17], "color": [236,  81,  57]},
    {"value": TEMP_VALUES[18], "color": [237,  42,  42]},
    {"value": TEMP_VALUES[18], "color": [195,  32,  39]},
    {"value": TEMP_VALUES[20], "color": [155,  27,  29]}
]

# Pressure scale using the
# same colours as the temperature scale
PRESSURE_VALUES = calc_steps(970, 1040, 21)
PRESSURE_SCALE = [
    {"value": PRESSURE_VALUES[0], "color": [ 29,  70, 154]},
    {"value": PRESSURE_VALUES[1], "color": [ 20,  98, 169]},
    {"value": PRESSURE_VALUES[2], "color": [ 22, 116, 182]},
    {"value": PRESSURE_VALUES[3], "color": [ 54, 138, 199]},
    {"value": PRESSURE_VALUES[4], "color": [ 63, 163, 218]},
    {"value": PRESSURE_VALUES[5], "color": [ 78, 192, 238]},
    {"value": PRESSURE_VALUES[6], "color": [174, 220, 216]},
    {"value": PRESSURE_VALUES[7], "color": [168, 214, 173]},
    {"value": PRESSURE_VALUES[8], "color": [158, 208, 127]},
    {"value": PRESSURE_VALUES[9], "color": [174, 211,  82]},
    {"value": PRESSURE_VALUES[10], "color": [208, 217,  62]},
    {"value": PRESSURE_VALUES[11], "color": [252, 222,   4]},
    {"value": PRESSURE_VALUES[12], "color": [251, 203,  12]},
    {"value": PRESSURE_VALUES[13], "color": [252, 183,  22]},
    {"value": PRESSURE_VALUES[14], "color": [250, 163,  26]},
    {"value": PRESSURE_VALUES[15], "color": [246, 138,  31]},
    {"value": PRESSURE_VALUES[16], "color": [242, 106,  47]},
    {"value": PRESSURE_VALUES[17], "color": [236,  81,  57]},
    {"value": PRESSURE_VALUES[18], "color": [237,  42,  42]},
    {"value": PRESSURE_VALUES[19], "color": [195,  32,  39]},
    {"value": PRESSURE_VALUES[20], "color": [155,  27,  29]}
]

# CO2 scale using the
# same colours as the temperature scale
CO2_VALUES = calc_steps(400, 1000, 5)
CO2_SCALE = [
    {"value": CO2_VALUES[0], "color": [  0,   0, 255]},
    {"value": CO2_VALUES[1], "color": [  0, 255,   0]},
    {"value": CO2_VALUES[2], "color": [255, 128,  50]},
    {"value": CO2_VALUES[3], "color": [255,   0,   0]},
    {"value": CO2_VALUES[4], "color": [200,   0,   0]},
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


def set_color(blink, temp, pressure, co2):
    temp_rgb = get_color(temp, TEMP_SCALE, 'rgb')
    #pressure_rgb = get_color(pressure, PRESSURE_SCALE, 'rgb')
    co2_rgb = get_color(co2, CO2_SCALE, 'rgb')
    
    blink.fade_to_rgb(1000, temp_rgb[0], temp_rgb[1], temp_rgb[2], 1)
    #blink.fade_to_rgb(1000, pressure_rgb[0], pressure_rgb[1], pressure_rgb[2], 2)
    blink.fade_to_rgb(1000, co2_rgb[0], co2_rgb[1], co2_rgb[2], 2)

with open('config.toml') as c:
    config = toml.load(c)

with blink1() as blink:
    while True:
        try:
            response = requests.get(config['source_url'])
            response.raise_for_status()
            netatmo_json = response.json()['devices'][0]

            temperature = float(netatmo_json['modules'][0]['dashboard_data']['Temperature'])
            pressure = float(netatmo_json['dashboard_data']['Pressure'])
            co2 = int(netatmo_json['modules'][1]['dashboard_data']['CO2'])
            rain = float(netatmo_json['modules'][2]['dashboard_data']['sum_rain_24'])
            rain1 = float(netatmo_json['modules'][2]['dashboard_data']['sum_rain_1'])

            if config['debug']:
                print(f'{temperature}, {pressure}, {co2}, {rain} {rain1:.1f}')
                
            set_color(blink, temperature, pressure, co2)

            with open(config['temperature_output_file'], 'w') as out:
                temp_color = get_color(temperature, TEMP_SCALE, 'hex')
                out.write(f'{temperature}°C\n\n{temp_color}')

            with open(config['pressure_output_file'], 'w') as out:
                pressure_color = get_color(pressure, PRESSURE_SCALE, 'hex')
                out.write(f'{pressure}hPa\n\n{pressure_color}')

            with open(config['co2_output_file'], 'w') as out:
                co2_color = get_color(co2, CO2_SCALE, 'hex')
                out.write(f'{co2}ppm\n\n{co2_color}')

            with open(config['rain_output_file'], 'w') as out:
                if rain1 > 0:
                    out.write(f'({rain1:.1f}) {rain}mm\n\n#0cc2dd')
                else:
                    out.write(f'{rain}mm\n\n#0cc2dd')

            if config['debug']:
                print(f'{temp_color}, {pressure_color}, {co2_color}\n')


        except Exception as e:
            print(traceback.format_exc())

        time.sleep(int(config['update_interval']))
