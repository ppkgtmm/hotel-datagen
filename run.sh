apt update && apt install -y python3 python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 generate.py
python3 stage.py
