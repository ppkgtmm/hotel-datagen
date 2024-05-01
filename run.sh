python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export SEED_DIR=$1
python3 generate.py
