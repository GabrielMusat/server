from aiohttp import web
import aiohttp_cors
from logger import Logger
import base64
import json
import time
import socketio
import asyncio
import os
import sys
import sanity_checker
assert len(sys.argv) == 3, Exception('admin username should be first arg and password should be second arg')

logger = Logger('server')

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()

if not os.path.isdir('data'): os.mkdir('data')
if not os.path.isdir('data/gcodes'): os.mkdir('data/gcodes')
if not os.path.isdir('data/users'): os.mkdir('data/users')

config = json.load(open('artenea_server.json'))

printers = {}


@sio.event
async def connect(sid, env):
    printers[env['name']] = {'sid': sid, 'response': None, 'status': None}
    logger.info(f'{env["name"]}\'s pandora is connected :)')


@sio.event
async def response(sid, data):
    printers[data['user']]['response'] = data['response']
    logger.info(f'{data["user"]}\'s pandora has returned a response: {data["response"]}')


@sio.event
async def status(sid, data):
    printers[data['user']]['status'] = data['status']


@sio.event
async def disconnect(sid):
    for user in printers:
        if printers[user]['sid'] == sid:
            logger.info(f'{user}\'s printer disconnected :(')
            del printers[user]
            return
    else:
        logger.error(f'{sid} not found in printers, could not disconnect')


@web.middleware
async def auth(request, handler):
    try:
        assert 'Authorization' in request.headers, Exception('Authorization not in headers')
        authorization = request.headers['Authorization']
        assert 'Basic ' == authorization[:6], Exception('not a basic auth')
        auth = base64.b64decode(authorization[6:]).decode()
        user, password = auth.split(':')
        if user == sys.argv[1]:
            assert password == sys.argv[2], Exception('incorrect password')
            request['admin'] = True
        else:
            request['admin'] = False
            assert user in [u.replace('.json', '') for u in os.listdir('data/users')], Exception('User not found')
            real_password = json.load(open(f'data/users/{user}.json'))['password']
            assert real_password == password, Exception('incorrect password')
        request['username'] = user

    except Exception as e:
        logger.warning(f'unauthorized request: {e}')
        return web.Response(status=401)

    return await handler(request)


async def register(request):
    logger.info(f'user {request["username"]} requests a register', color='OKBLUE')
    if not request['admin']:
        logger.warning(f'user {request["username"]} is not admin')
        return web.Response(status=401)
    try:
        user = await request.json()
    except Exception as e:
        logger.warning(f'request body must be a json: {e}')
        return web.Response(text='request body must be a json', status=400)

    for param in ['name', 'password']:
        if param not in user:
            logger.warning(f'"{param}" parameter must be in json')
            return web.Response(text=f'"{param}" parameter must be in json', status=400)

    existing_users = [u.replace('.json', '') for u in os.listdir('data/users')]
    if user['name'] in existing_users:
        logger.warning(f'trying to register {user["name"]} while it is already registered')
        return web.Response(text=f'user {user["name"]} already registered', status=400)
    else:
        json.dump({'password': user['password'], 'rights': []}, open(f'data/users/{user["name"]}.json', 'w'))
        logger.info(f'user {user["name"]} with password {user["password"]} registered correctly', color='OKGREEN')
        return web.Response(text='ok', status=200)


async def users(request):
    return web.json_response([u.replace('.json', '') for u in os.listdir('data/users')])


async def gcodes(request):
    return web.json_response(os.listdir('data/gcodes'))


async def rights(request):
    logger.info(f'user {request["username"]} request a new right association', color='OKBLUE')
    if not request['admin']:
        logger.warning(f'user {request["username"]} is not admin')
        return web.Response(status=401)
    try:
        right = await request.json()
    except Exception as e:
        logger.warning(f'request body must be a json: {e}')
        return web.Response(text='request body must be a json', status=400)

    for param in ['user', 'file']:
        if param not in right:
            logger.warning(f'"{param}" parameter must be in json')
            return web.Response(text=f'"{param}" parameter must be in json', status=400)

    if right['file'] not in os.listdir('data/gcodes'):
        logger.warning(f'gcode {right["gcode"]} does not exists')
        return web.Response(text=f'gcode {right["file"]} does not exists', status=400)

    if right['user'] not in [u.replace('.json', '') for u in os.listdir('data/users')]:
        logger.warning(f'user {right["user"]} does not exist')
        return web.Response(text=f'user {right["user"]} does not exist', status=400)

    user = json.load(open(f'data/users/{right["user"]}.json'))
    if right['file'] in user['rights']:
        logger.warning(f'user {right["user"]} already has right to {right["file"]}')
        return web.Response(text=f'user {right["user"]} already has right to {right["file"]}', status=400)
    else:
        user['rights'].append(right['file'])
        json.dump(user, open(f'data/users/{right["user"]}.json', 'w'))
        logger.info(f'user {right["user"]} now has the right to print {right["file"]}', color='OKGREEN')
        return web.Response(text='ok', status=200)


async def checkrights(request):
    logger.info(f'user {request["username"]} requests to know its rights', color='OKBLUE')
    username = request['username']
    if username not in [u.replace('.json', '') for u in os.listdir('data/users')]:
        logger.warning(f'user {username} does not exist')
        return web.Response(text=f'user {username} does not exist', status=400)
    rights = json.load(open(f'data/users/{username}.json'))['rights']
    logger.info(f'user {request["username"]} has rights to: {rights}', color='OKGREEN')
    return web.json_response(rights)


async def stats(request):
    logger.info(f'user {request["username"]} requests to know its stats', color='OKBLUE')
    username = request['username']
    if username not in [u.replace('.json', '') for u in os.listdir('data/users')]:
        logger.warning(f'user {username} does not exist')
        return web.Response(text=f'user {username} does not exist', status=400)
    if request['username'] not in printers:
        logger.info(f'{request["username"]}\'s pandora is not connected')
        return web.Response(text=f'{request["username"]}\'s pandora is not connected', status=400)

    status = printers[username]['status']
    logger.info(f'user {request["username"]}\'s stats are {status}')
    return web.json_response(status) if status else web.Response(text=f'status unknown', status=400)


async def add(request):
    logger.info(f'user {request["username"]} requests to add an instruction')
    try:
        instruction = await request.json()
    except Exception as e:
        logger.warning(f'request body must be a json: {e}')
        return web.Response(text='request body must be a json', status=400)
    try:
        sanity_checker.check_add(instruction)
    except Exception as e:
        logger.warning(f'error adding instruction: {e}')
        return web.Response(text=str(e), status=400)

    if request['username'] not in printers:
        logger.info(f'{request["username"]}\'s pandora is not connected')
        return web.Response(text=f'{request["username"]}\'s pandora is not connected', status=400)

    await sio.emit('instruction', instruction, to=printers[request['username']])
    logger.info(f'instruction {instruction} sent correctly to {request["username"]}\'s printer', color='OKGREEN')
    if config['wait_responses']:
        start = time.time()
        while True:
            if printers[request["username"]]['response']:
                r = printers[request["username"]]['response']
                return web.Response(text=r, status=200 if r == 'ok' else 400)
            elif time.time() - start > 5:
                logger.warning(f'timeout waiting for response to instruction {instruction} of {request["username"]}\'s printer')
                return web.Response(text='timeout waiting for printer response', status=400)
            await asyncio.sleep(0.25)
    else:
        return web.Response(text='ok')


async def upload(request):
    logger.info(f'user {request["username"]} requests a file upload', color='OKBLUE')
    reader = await request.multipart()
    file = await reader.next()
    if file.name != 'file':
        logger.warning(f'file key {file.name} is not valid, only "file" is allowed')
        return web.Response(text=f'file key {file.name} is not valid, only "file" is allowed', status=400)

    if file.filename[-6:] != '.gcode':
        logger.warning(f'file {file.filename} is not a gcode')
        return web.Response(text=f'file {file.filename} is not a gcode', status=400)

    gcode_path = os.path.join('data', 'gcodes', file.filename)
    with open(gcode_path, 'wb') as f:
        while True:
            chunk = await file.read_chunk()
            if not chunk: break
            f.write(chunk)

    logger.info(f'file {file.filename} uploaded correctly', color='OKGREEN')
    return web.Response(text='ok')


async def download(request):
    logger.info(f'user {request["username"]} requests a file download', color='OKBLUE')
    params = request.rel_url.query
    for param in ['file']:
        if param not in params:
            logger.warning(f'"{param}" parameter must be in query parameters')
            return web.Response(text=f'"{param}" parameter must be in query parameters', status=400)

    filepath = os.path.join('data', 'gcodes', params['file'])
    if not os.path.isfile(filepath):
        logger.warning(f'file {params["file"]} does not exist')
        return web.Response(text=f'file {params["file"]} does not exist', status=400)

    user_rights = json.load(open(f'data/users/{request["username"]}.json'))['rights']
    if params['file'] not in user_rights:
        logger.warning(f'user {request["username"]} has no right to download {params["file"]}')
        return web.Response(text=f'user {request["username"]} has no right to download {params["file"]}', status=400)

    logger.info(f'sending file {params["file"]} to {request["username"]}\'s printer', color='OKGREEN')
    return web.FileResponse(filepath)

app.middlewares.append(auth)
app.router.add_routes([
    web.post('/register', register),
    web.get('/users', users),
    web.get('/gcodes', gcodes),
    web.post('/rights/give', rights),
    web.get('/rights/check', checkrights),
    web.get('/stats', stats),
    web.post('/add', add),
    web.post('/upload', upload)
])

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app, host=config['host'], port=config['port'])
