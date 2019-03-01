import os


accepted_instructions = ['home', 'print', 'download', 'command']


def check_add(json_decoded):
    assert 'instruction' in json_decoded, Exception('"instruction" parameter must be present in json')
    assert json_decoded['instruction'] in accepted_instructions, Exception(f'instruction value is {json_decoded["instruction"]}, but must be one of these: {accepted_instructions}')
    if json_decoded['instruction'] == 'download':
        assert os.path.isfile(os.path.join('gcodes', json_decoded['filename'])), Exception(f'file {json_decoded["filename"]} not in server, avaible gcodes are: {os.listdir("gcodes")}')
    if json_decoded['instruction'] == 'print':
        assert 'filename' in json_decoded, Exception('filename parameter not found, filename parameter must be set with one of the avaiable gcodes in server')
        assert os.path.isfile(os.path.join('gcodes', json_decoded['filename'])), Exception(f'file {json_decoded["filename"]} not in server, avaiable gcodes are {os.listdir("gcodes")}')
    if json_decoded['instruction'] == 'command':
        assert 'command' in json_decoded, Exception('command parameter not found, command parameter must be set in json with a valid Marlin firmware gcode')
