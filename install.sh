#!/usr/bin/env bash

cd /var/www/server

sudo apt install python3-pip -y

sudo apt install python3-venv -y

sudo apt-get install python3-dev -y

python3 -m venv venv

source venv/bin/activate

pip3 install wheel

pip3 install -r requirements.txt

echo "
#!/usr/bin/env bash
cd /var/www/server
source venv/bin/activate
python3 server.py
" > server.sh

sudo chmod +x server.sh
sudo mv server.sh /usr/bin/server

sudo touch /etc/systemd/system/server.service
sudo chmod 775 /etc/systemd/system/server.service
sudo chmod a+w /etc/systemd/system/server.service

sudo echo "
[Unit]
Description=zi
[Service]
User=root
ExecStart=/bin/bash /usr/bin/server
Restart=on-failure
WorkingDirectory=/
StandardOutput=syslog
StandardError=syslog
[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/server.service

sudo systemctl enable server.service
sudo systemctl daemon-reload