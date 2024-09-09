# build_files.sh

sudo apt update
sudo apt install -y software-properties-common

# Add the deadsnakes PPA which contains Python 3.10
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.10 and pip
sudo apt install -y python3.10 python3.10-venv python3.10-dev
sudo apt install -y python3-pip

pip install -r requirements.txt
python3.9 manage.py collectstatic --noinput
