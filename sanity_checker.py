import os


accepted_instructions = ['home', 'print', 'download', 'command', 'move', 'load', 'unload']


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