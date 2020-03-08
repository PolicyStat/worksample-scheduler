import mimetypes
import pathlib

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404

from project.models import WorkSampleTemplate, WorkSample


class WorkSampleTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'description',
        'is_active',
        'allowed_minutes',
        'email_recipients',
        'created',
        'modified',
        'created_by_user',
    )

    exclude = ('created_by_user', )

    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'created_by_user'):
            obj.created_by_user = request.user
        super().save_model(request, obj, form, change)


class WorkSampleAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'access_url',
        'template',
        'applicant_name',
        'applicant_email',
        'start_time',
        'finish_time',
        'minutes',
        'download_url',
        'created',
        'modified',
        'created_by_user',
    )
    fields = (
        'template',
        'applicant_name',
        'applicant_email',
        'start_time',
        'finish_time',
    )

    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'created_by_user'):
            obj.created_by_user = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        # https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_urls
        # https://github.com/django/django/blob/stable/2.2.x/django/contrib/admin/options.py#L601
        urls = super().get_urls()
        admin_view = self.admin_site.admin_view
        my_urls = [
            path('<uuid:uuid>/download', admin_view(self.download), name='worksample_download')
        ]
        return my_urls + urls

    def download(self, request, uuid):
        worksample = get_object_or_404(self.model, uuid=uuid)
        content_type, encoding = mimetypes.guess_type(worksample.submission_file_name)
        response = HttpResponse(worksample.submission, content_type=content_type)
        suffix = pathlib.Path(worksample.submission_file_name).suffix
        file_name = worksample.applicant_name.lower().replace(' ', '_') + suffix
        disposition = f'attachment; filename="{file_name}"'
        response['Content-Disposition'] = disposition
        response['Content-Length'] = len(worksample.submission)
        return response

    def access_url(self, obj):
        path = obj.get_absolute_url()
        return format_html(f'<a href="{path}">URL</a>')

    def minutes(self, obj):
        delta_minutes = obj.get_time_spent_in_minutes()
        if delta_minutes is None:
            return ''
        return '{:.2f}'.format(delta_minutes)

    def download_url(self, obj):
        if obj.submission is None:
            return ''
        download_url = reverse('admin:worksample_download', kwargs=dict(uuid=obj.uuid))
        return format_html(f'<a href="{download_url}">Download</a>')


admin.site.register(WorkSampleTemplate, WorkSampleTemplateAdmin)
admin.site.register(WorkSample, WorkSampleAdmin)
