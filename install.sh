#!/bibn/bash

wget https://raw.githubusercontent.com/chibike/shell_scripts/master/ubuntu_essentials.sh
chmod +x ubuntu_essentials.sh
./ubuntu_essentials.sh
rm ubuntu_essentials.sh
sudo apt-get install python3-pip
git clone https://github.com/chibike/fdd_machine_monitor_project.git
cd fdd_machine_monitor_project
python3 -m pip install -r requirements.txt
