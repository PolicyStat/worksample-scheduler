# Work Sample Scheduler

## Local Quick start

```
ln -s dev.env .env
pipenv install --dev --python=3.6
pipenv shell

python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py runserver
```

## Heroku Quick Deploy

```
heroku create

ln -s dev.env .env
pipenv install --dev --python=3.6
pipenv shell
heroku addons:attach heroku-postgresql:hobby-dev
heroku config:set DJANGO_SECRET_KEY=$(python manage.py generate_secret_key)
heroku config:set DJANGO_ALLOWED_HOSTS='<appname>.herokuapp.com'
heroku config:set DJANGO_SECURE_SSL_HOST='<appname>.herokuapp.com'
heroku config:set DJANGO_DEBUG=yes

git push heroku master

heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku open
```

## Enable email

### 1. Attach SendGrid Heroku Add-on

This will only work if your Heroku account
has a credit card added.
The add-on is still free.
The credit card is just to verify your identity.

```
heroku addons:create sendgrid:starter
```

### 2. Access SendGrid

From your Heroku app dashboard,
click on the SendGrid app.
This will redirect you
to SendGrid's website
and automatically log you in.

### 3. Create an API key

Create an API key with Restricted Access: Mail Send

See: https://sendgrid.com/docs/User_Guide/Settings/api_keys.html

### 4. Tell Heroku what the key is

```
heroku config:set SENDGRID_API_KEY=...
```

### 5. Remove unused SENDGRID Heroku configs

When the SendGrid add-on is created,
it adds credentials to the configuration
that we don't need anymore

```
heroku config:unset SENDGRID_USERNAME SENDGRID_PASSWORD
```

### 6. (optional) Create another API key for local use

Follow the applicable steps above,
and add the key to `dev.env`.
