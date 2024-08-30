python3 -m venv venv
source venv/bin/activate


pip install -r requirements.txt
Python manage.py makemigrations
Python manage.py migrate
Python manage.py collectstatic --noinput