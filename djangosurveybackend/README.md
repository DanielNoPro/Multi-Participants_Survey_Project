# django_survey_backend

## Familiar with models and admin

- Create folder and activate environment:
```cmd
py -m venv venv
```
- Activate the virtual environment:
```cmd
venv\Scripts\activate
```
- Install Django:
    - pip install django
- Start new project: django-admin startproject core .
    + manage.py allow to access django admin
- Build a new app:
    + python manage.py startapp [app_name]
    + setting file in app store: declare the project that it depend on
- declare model in file models.py in app folder declare. -> run migrate
- config the media folder in core setting file:
- config the URL in core Url file
- Create superuser
- Run server

## Open API schema
Refer : https://drf-spectacular.readthedocs.io/en/latest/readme.html

- To generate new schema:
```cmd
python manage.py spectacular --color --file schema.yml
```


## Testing -> Models

- Run python test: python manage.py test
- install coverage to management test: pip install coverage
- run command line:coverage run manage.py test
- Report:coverage report
- coverage run --omit='*/venv/*' manage.py test
- coverage html

## Create url file in application

- config url in project file urls.py

====== Part 2 ===========

1. Refactoring
2. Introducing session (optional)
3. Development
4. Testing

```cmd
pip freeze > requirements.txt 
```

To migrate database
```cmd
python manage.py makemigrations
python manage.py migrate
```

To create super user
```cmd
python manage.py createsuperuser
```

To check error
```cmd
flake8 . --max-line-length=127
```