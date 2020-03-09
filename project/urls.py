from django.contrib import admin
from django.urls import path, include

import project.views

urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
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
]
