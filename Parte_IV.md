

## Heroku
como funciona: https://dzone.com/articles/how-heroku-works
[configuracoes basicas](https://devcenter.heroku.com/articles/django-app-configuration):
Heroku web applications require a Procfile.
This file is used to explicitly declare your application’s process types and entry points. It is located in the root of your repository.
```commandline
#Procfile
web: gunicorn myproject.wsgi
```
This Procfile requires Gunicorn, the production web server that we recommend for Django applications. 

> Be sure to add gunicorn to your requirements.txt file as well

settings.py changes
On Heroku, sensitive credentials are stored in the environment as config vars. This includes database connection information (named DATABASE_URL), which is traditionally hardcoded in Django applications.

#### o que é gunicorn
Web applications that process incoming HTTP requests concurrently make much more efficient use of dyno resources than web applications that only process one request at a time. Because of this, we recommend using web servers that support concurrent request processing whenever developing and running production services.

The Django and Flask web frameworks feature convenient built-in web servers, but these blocking servers only process a single request at a time. If you deploy with one of these servers on Heroku, your dyno resources will be underutilized and your application will feel unresponsive.

Gunicorn is a pure-Python HTTP server for WSGI applications. It allows you to run any Python application concurrently by running multiple Python processes within a single dyno. It provides a perfect balance of performance, flexibility, and configuration simplicity.
[source](https://devcenter.heroku.com/articles/python-gunicorn)  

#### configurando variáveis de ambiente

[source](https://devcenter.heroku.com/articles/config-vars)

## reflexões
## Heroku
como funciona: https://dzone.com/articles/how-heroku-works


## reflexões

[The most important part of a function name is a verb. ](https://melevir.medium.com/python-functions-naming-the-algorithm-74320a18278d)
[The most important part of a function name is a verb. ](https://melevir.medium.com/python-functions-naming-the-algorithm-74320a18278d)