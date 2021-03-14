# Prototype of a django project using leaflet

#### Criando ambiente de desenvolvimento:

```python
python -m venv .djleaflet
pip install --upgrade pip
pip install -r requirements.txt
django-admin startproject mapProje .
cd mapProj
manage startapp core
manage migrate
manage createsuperuser
```
#### Add installed apps

```python
# setting.py
INSTALLED_APPS = [
    ...
    'mapProj.core',
    'leaflet',
]
```

#### Create model

First thing that i bielieve would worth test: if model has geom atribute, and its type.

##### Register model on admin

This could be validate as well.

```python
from leaflet.admin import LeafletGeoAdmin
from .models import model

```

#### Add statics root

```python
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR
```