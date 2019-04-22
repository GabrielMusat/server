#!/usr/bin/env bash

cd ~/server

sudo apt install python3-pip -y

sudo apt install python3-venv -y

sudo apt-get install python3-dev -y

python3 -m venv venv

source ~/server/venv/bin/activate

pip3 install wheel

pip3 install -r requirements.txt

echo "
#!/usr/bin/env bash
source ~/server/venv/bin/activate
cd ~/server
python3 server.py
" > server.sh

sudo chmod +x server.sh
sudo mv server.sh /bin/server

sudo touch /etc/systemd/system/server.service
sudo chmod 775 /etc/systemd/system/server.service
sudo chmod a+w /etc/systemd/system/server.service

sudo echo "
[Unit]
Description=zi
[Service]
User=pablo_3pol
ExecStart=/bin/bash /bin/server
Restart=on-failure
WorkingDirectory=~/server
StandardOutput=syslog
StandardError=syslog
[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/server.service

sudo systemctl enable server.service
sudo systemctl daemon-reload