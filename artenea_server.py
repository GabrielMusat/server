from flask import Flask, request, send_file
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS, cross_origin
from OpenSSL import SSL
import json
import os

config = json.loads(open('artenea_server.conf').read())
users = json.loads(open('UsersDDBB.conf').read())
admins = json.loads(open('AdminsDDBB.conf').read())

# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('yourserver.key')
# context.use_certificate_file('yourserver.crt')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
auth_user = HTTPBasicAuth()
auth_admin = HTTPBasicAuth()

buffer_out = {}
buffer_in = {}
for user_name in users:
    buffer_out[user_name] = []
    buffer_in[user_name] = {'temp': -1, 'job': -1}


@auth_user.get_password
def get_pw(username):
    if username in users:
        return users[username]
    return None


@auth_admin.get_password
def get_pw(username):
    if username in admins:
        return admins[username]
    return None


@app.route('/')
@auth_admin.login_required
def test():
    return 'ok'


@app.route('/register', methods=['POST'])
@auth_admin.login_required
@cross_origin()
def register():
    try:
        new_users = json.loads(request.data)
        for new_user in new_users:
            if new_user in users:
                print('user already registered')
            else:
                users[new_user] = new_users[new_user]
                buffer_out[new_user] = []
                with open('UsersDDBB.conf', 'w') as UsersDDBB:
                    UsersDDBB.write(json.dumps(users, indent=4))

                print(f'new user {new_user} registered correctly')

        return 'ok'

    except Exception as e:
        print('new user registration failed')
        print(e)

        return 'failed'


@app.route('/users', methods=['GET'])
@cross_origin()
def get_users():
    return json.dumps(users, indent=4)


@app.route('/gcodes', methods=['GET'])
@auth_user.login_required
@cross_origin()
def get_files():
    user = auth_user.username()
    return json.dumps(os.listdir('gcodes'))


@app.route('/rights', methods=['POST'])
@auth_admin.login_required
@cross_origin()
def give_rigths():
    right = json.loads(request.data)
    user = [k for k in right][0]
    gcode = right[user]
    if gcode not in os.listdir('gcodes'):
        return f'gcode {gcode} not uploaded to server'
    folder = 'users'
    if not os.path.exists(folder): os.makedirs(folder)
    user_json_path = os.path.join(folder, user + '.json')
    if not os.path.isfile(user_json_path):
        user_json = {'rights': [gcode]}
        with open(user_json_path, 'w') as f:
            f.write(json.dumps(user_json, indent=4))
    else:
        user_json = json.loads(open(user_json_path, 'r').read())
        if gcode in user_json['rights']:
            return f'user {user} already have gcode rights to {gcode}'
        user_json['rights'].append(gcode)
        with open(user_json_path, 'w') as f:
            f.write(json.dumps(user_json, indent=4))

    return f'user {user} gcode rights: {json.dumps(user_json["rights"])}'


@app.route('/checkrights', methods=['GET'])
@auth_user.login_required
@cross_origin()
def check_rights():
    user = auth_user.username()
    user_json_path = os.path.join('users', user + '.json')
    if os.path.isfile(user_json_path):
        user_json = json.loads(open(user_json_path, 'r').read())
        return f'user {user} gcode rights: {json.dumps(user_json["rights"])}'
    else:
        return f'user {user} has no gcode rights'


@app.route('/buffer', methods=['GET'])
@auth_user.login_required
@cross_origin()
def return_buffer():
    global buffer_out
    global buffer_in
    user = auth_user.username()
    buffer_in[user] = {'temp': request.args.get('temp'), 'job': request.args.get('job')}
    if len(buffer_out[user]) > 0:
        to_return = buffer_out[user][0]
        print('sending instruction and deleting it from buffer')
        del buffer_out[user][0]
        return to_return

    else:
        return json.dumps({'instruction': 'None'})


@app.route('/stats', methods=['GET'])
@auth_user.login_required
@cross_origin()
def stats():
    global buffer_in
    user = auth_user.username()
    return json.dumps(buffer_in[user], indent=4)


@app.route('/full_stats', methods=['GET'])
@auth_admin.login_required
@cross_origin()
def full_stats():
    global buffer_in
    return json.dumps(buffer_in,  indent=4)


@app.route('/add', methods=['POST'])
@auth_user.login_required
@cross_origin()
def add_to_buffer():
    global buffer_out
    try:
        json_instruction = request.data
        user = auth_user.username()
        buffer_out[user].append(json_instruction)
        print('json added to buffer')
        return json.dumps({'status': 'ok'})

    except Exception as e:
        print('error adding instruction to buffer:')
        print(e)
        return json.dumps({'status': 'could not add instruction to buffer', 'error': str(e)})


@app.route('/upload', methods=['POST'])
@auth_admin.login_required
@cross_origin()
def upload_file():
    try:
        folder = 'gcodes'
        file = request.files['file']
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'gcode':
            if not os.path.exists(folder): os.makedirs(folder)
            file.save(os.path.join(folder, file.filename))
            return f'g-code {file.filename} uploaded correctly'

        else:
            return 'only .gcode files are allowed'

    except Exception as e:
        print('error al subir gcode: ' + str(e))
        return 'error uploading g-code: ' + str(e)


@app.route('/download', methods=['GET'])
@auth_user.login_required
@cross_origin()
def download_file():
    try:
        user = auth_user.username()
        filename = request.args.get('filename')
        folder = 'gcodes'
        if not os.path.exists(folder):
            return f'there are no g-codes in the server'

        file_path = os.path.join(folder, filename)
        if not os.path.isfile(file_path):
            return f'g-code {filename} is not in the server'

        user_json_path = os.path.join('users', user + '.json')
        if not os.path.isfile(user_json_path):
            return f'user {user} has no right to print this g-code'
        else:
            user_json = json.loads(open(user_json_path, 'r').read())
            if filename in user_json['rights']:
                return send_file(file_path)
            else:
                return f'user {user} has no right to print this g-code'

    except Exception as e:
        print('error al mandar gcode a impresora: ' + str(e))
        return 'error al mandar gcode a impresora: ' + str(e)


if __name__ == '__main__':
    app.run(host=config['Artenea_host'], port=config['Artenea_port'])
