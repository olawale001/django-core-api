python3 -m venv venv
source venv/bin/activate


pip install -r requirements.txt
Python3.9 manage.py makemigrations
Python3.9 manage.py migrate
Python3.9 manage.py collectstatic