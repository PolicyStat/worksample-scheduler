"""
Django settings

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

from configurations import Configuration, values


class Common(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SECRET_KEY = values.SecretValue()
    DEBUG = values.BooleanValue(True)
    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'whitenoise.runserver_nostatic',
        'django.contrib.staticfiles',

        'django_extensions',
        'project',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'project.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': False,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                'loaders': (
                    'hamlpy.template.loaders.HamlPyFilesystemLoader',
                    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
                ),
            },
        },
    ]

    CKEDITOR_CONFIGS = {
        'admin': {
            'toolbar': 'custom',
            'toolbar_custom': [
                {'name': 'document', 'items': ['Source']},
                {'name': 'clipboard', 'items': [
                    'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-',
                    'Undo', 'Redo'
                ]},
                {'name': 'editing', 'items': [
                    'Find', 'Replace', '-', 'SelectAll', '-', 'Scayt',
                ]},
                {'name': 'styles', 'items': ['Styles', 'Format']},
                '/',
                {'name': 'basicstyles', 'items': [
                    'Bold', 'Italic', 'Underline', 'Strike', 'Subscript',
                    'Superscript', '-', 'CopyFormatting', 'RemoveFormat',
                ]},
                {'name': 'paragraph', 'items': [
                    'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent',
                    '-', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter',
                    'JustifyRight', 'JustifyBlock',
                ]},
                {'name': 'links', 'items': ['Link', 'Unlink']},
                {'name': 'insert', 'items': ['Table', 'HorizontalRule']},
            ],
        },
    }

    WSGI_APPLICATION = 'project.wsgi.application'

    DATABASES = values.DatabaseURLValue(
        'sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    )

    # Password validation
    # https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/
    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = values.Value(None, environ_prefix=None)
    SERVER_EMAIL = values.Value(None)
    # DJANGO_ADMINS=Bob,bob@bob.com;Dave,dave@dave.com
    ADMINS = values.SingleNestedTupleValue([])


class Development(Common, Configuration):
    INTERNAL_IPS = [
        '127.0.0.1',
    ]
    AUTH_PASSWORD_VALIDATORS = []
    # Use the sendgrid API, but don't actually deliver emails
    SENDGRID_SANDBOX_MODE_IN_DEBUG = values.BooleanValue(True)


class Production(Common, Configuration):
    DEBUG = False
    ALLOWED_HOSTS = values.ListValue([], separator=' ')
    SESSION_COOKIE_SECURE = values.BooleanValue(False)
    SECURE_BROWSER_XSS_FILTER = values.BooleanValue(True)
    SECURE_CONTENT_TYPE_NOSNIFF = values.BooleanValue(True)
    SECURE_SSL_REDIRECT = values.BooleanValue(False)
    SECURE_SSL_HOST = values.Value(None)
    CSRF_COOKIE_DOMAIN = values.Value(None)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SENDGRID_API_KEY = values.Value(None, environ_prefix=None, environ_required=True)
