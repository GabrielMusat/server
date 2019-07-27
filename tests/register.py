import requests
import sys

assert len(sys.argv) == 4, Exception('url must be passed as first arg, username as second arg and password as third arg')
url = sys.argv[1]
auth = (sys.argv[2], sys.argv[3])


def test():
    testname = 'not admin'
    r = requests.post(url + '/register', data='{"name": "Carmen", "password": "contrasenaC}', auth=('Carmen', 'contrasenaC'))
    assert r.status_code == 401, Exception(f'{testname} test not passed')
    print(f'[1/] OK: {testname} test passed')

    testname = 'bad formed json'
    r = requests.post(url+'/register', data='{"name": "Carmen", "password": "contrasenaC}', auth=auth)
    assert r.status_code == 400, Exception(f'{testname} test not passed')
    print(f'[2/] OK: {testname} test passed')

    testname = 'missing one param'
    r = requests.post(url + '/register', data='{"name": "Carmen"}', auth=auth)
    assert r.status_code == 400, Exception(f'{testname} test not passed')
    print(f'[3/] OK: {testname} test passed')

    testname = 'registration correct'
    r = requests.post(url + '/register', data='{"name": "Carmen", "password": "contrasenaC"}', auth=auth)
    assert r.status_code == 200, Exception(f'{testname} test not passed')
    print(f'[4/] OK: {testname} test passed')

    testname = 'user already exists'
    r = requests.post(url + '/register', data='{"name": "Carmen", "password": "contrasenaC"}', auth=auth)
    assert r.status_code == 400, Exception(f'{testname} test not passed')
    print(f'[5/] OK: {testname} test passed')


if __name__ == '__main__':
    test()
