# dj-coffeeAPP
A backend for an app for posting
reviews of coffee drinks from different coffeeshops allowing rating
drink by descriptors, same authentification, filtering, swagger docs
and pagination, written in python + django-rest.

# How to run
1. Clone this Repository
2. Navigate to the directory with this README
3. Create virtualenv - Optional
```
python -m venv venv
source venv/bin/activate
# venv\Scripts\activate on Windows
```
4. Install the requirements for the package:
```
pip install -r requirements.txt
```
5. Apply migrations
```
python manage.py migrate
```
6. Create Superuser (optional)
```
python manage.py createsuperuser
```
7. Run the server
```
python manage.py runserver
```

# How to use
You can open swagger documentation on http://127.0.0.1:8000/swagger/ , all currently supported requests are documented there.
