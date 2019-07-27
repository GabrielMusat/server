import requests
import socketio
import sys

assert len(sys.argv) == 4, Exception('url must be passed as first arg, username as second arg and password as third arg')
url = sys.argv[1]
auth = (sys.argv[2], sys.argv[3])


def test():
    test_num = 1

    test_name = 'not admin'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url + '/register', data='{"name": "Carmen", "password": "contrasenaC}', auth=('Carmen', 'contrasenaC'))
    assert r.status_code == 401, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'bad formed json'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url+'/register', data='{"name": "Carmen", "password": "contrasenaC}', auth=auth)
    assert r.status_code == 400, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'missing one param'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url + '/register', data='{"name": "Carmen"}', auth=auth)
    assert r.status_code == 400, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'registration correct'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url + '/register', data='{"name": "Carmen", "password": "contrasenaC"}', auth=auth)
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'user already exists'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url + '/register', data='{"name": "Carmen", "password": "contrasenaC"}', auth=auth)
    assert r.status_code == 400, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'no gcodes stored'
    print(f'test {test_num}: {test_name}')
    r = requests.get(url + '/gcodes', auth=auth)
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    assert r.json() == [], Exception(f'expected response {[]} but got {r.json()}')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'upload gcode'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url + '/upload', files={'file': open('test.gcode', 'rb')}, auth=auth)
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'one gcode stored'
    print(f'test {test_num}: {test_name}')
    r = requests.get(url + '/gcodes', auth=auth)
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    assert r.json() == ['test.gcode'], Exception(f'expected response {["test.gcode"]} but got {r.json()}')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'user has no rights'
    print(f'test {test_num}: {test_name}')
    r = requests.get(url + '/rights/check', auth=('Carmen', 'contrasenaC'))
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    assert r.json() == [], Exception(f'expected response {[]} but got {r.json()}')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'give rights to user'
    print(f'test {test_num}: {test_name}')
    r = requests.post(url + '/rights/give', data='{"user": "Carmen", "file": "test.gcode"}', auth=auth)
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    print(f'OK: {test_name} test passed')
    test_num += 1

    test_name = 'user has right to one gcode'
    print(f'test {test_num}: {test_name}')
    r = requests.get(url + '/rights/check', auth=('Carmen', 'contrasenaC'))
    assert r.status_code == 200, Exception(f'{test_name} test not passed')
    assert r.json() == ['test.gcode'], Exception(f'expected response {["test.gcode"]} but got {r.json()}')
    print(f'OK: {test_name} test passed')
    test_num += 1


if __name__ == '__main__':
    test()
