#!/usr/bin/env bash

cd ~/artenea_server

sudo apt install python3-pip -y

sudo apt install python3-venv -y

sudo apt-get install python3-dev -y

python3 -m venv venv

source ~/venv/bin/activate

pip3 install wheel

pip3 install -r requirements.txt

echo "
#!/usr/bin/env bash
source ~/artenea_server/venv/bin/activate
cd ~/artenea_server
python3 artenea_server.py
" > artenea_server.sh

sudo chmod +x artenea_server.sh
sudo mv artenea_server.sh /bin/artenea_server

sudo touch /etc/systemd/system/artenea_server.service
sudo chmod 775 /etc/systemd/system/artenea_server.service
sudo chmod a+w /etc/systemd/system/artenea_server.service

sudo echo "
[Unit]
Description=zi
[Service]
User=pablo_3pol
ExecStart=/bin/bash /bin/artenea_server
Restart=on-failure
WorkingDirectory=~/artenea_server
StandardOutput=syslog
StandardError=syslog
[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/artenea_server.service

sudo systemctl enable artenea_server.service
sudo systemctl daemon-reload