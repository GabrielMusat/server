import os


accepted_instructions = ['home', 'print', 'cancel', 'download', 'command', 'move', 'load', 'unload', 'wifi', 'set_init_gcode']


def check_add(json_decoded):
    assert 'instruction' in json_decoded, Exception('"instruction" parameter must be present in json')
    assert json_decoded['instruction'] in accepted_instructions, Exception(f'instruction value is {json_decoded["instruction"]}, but must be one of these: {accepted_instructions}')
    if json_decoded['instruction'] == 'download':
        assert os.path.isfile(os.path.join('data', 'gcodes', json_decoded['file'])), Exception(f'file {json_decoded["file"]} not in server, avaible gcodes are: {os.listdir("data/gcodes")}')
    if json_decoded['instruction'] == 'print':
        assert 'file' in json_decoded, Exception('file parameter not found, file parameter must be set with one of the avaiable gcodes in server')
        assert os.path.isfile(os.path.join('data', 'gcodes', json_decoded['file'])), Exception(f'file {json_decoded["file"]} not in server, avaiable gcodes are {os.listdir("data/gcodes")}')
    if json_decoded['instruction'] == 'command':
        assert 'command' in json_decoded, Exception('command parameter not found, command parameter must be set in json with a valid Marlin firmware gcode')
    if json_decoded['instruction'] == 'move':
        assert 'axis' in json_decoded, Exception('axis parameter not found, move instruction must be passed with axis and distance parameters')
        assert 'distance' in json_decoded, Exception('distance parameter not found, move instruction must be passed with axis and distance parameters')
    if json_decoded['instruction'] == 'wifi':
        assert 'ssid' in json_decoded, Exception('ssid parameter not found, it must be set with the name of the wifi')
        assert json_decoded["ssid"] > 3, Exception('parámetro ssid incorrecto')
        assert 'psk' in json_decoded, Exception('psk parameter not found, it must be set with the the wifi`s password')
        assert json_decoded["psk"] > 3, Exception('parámetro ssid incorrecto')