"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import project.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', project.views.index, name='index'),
    path('worksample/<uuid:uuid>', project.views.worksample, name='worksample'),
    path(
        'worksample/<uuid:uuid>/start',
        project.views.start_worksample,
        name='start_worksample',
    ),
    path(
        'worksample/<uuid:uuid>/complete',
        project.views.complete_worksample,
        name='complete_worksample',
    ),
    path(
        'worksample/<uuid:uuid>/download',
        project.views.download_worksample_submission,
        name='download_worksample',
    ),
]
