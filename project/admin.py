from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

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
        'download',
        'created',
        'modified',
        'created_by_user',
    )
    fields = ('template', 'applicant_name', 'applicant_email')

    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'created_by_user'):
            obj.created_by_user = request.user
        super().save_model(request, obj, form, change)

    def access_url(self, obj):
        path = obj.get_absolute_url()
        return format_html('<a href="{path}">{path}</a>'.format(path=path))

    def minutes(self, obj):
        delta_minutes = obj.get_time_spent_in_minutes()
        if delta_minutes is None:
            return ''
        return '{:.2f}'.format(delta_minutes)

    def download(self, obj):
        if obj.submission is None:
            return ''
        download_url = reverse('download_worksample', kwargs=dict(uuid=obj.uuid))
        return format_html('<a href="{url}">Download</a>'.format(url=download_url))


admin.site.register(WorkSampleTemplate, WorkSampleTemplateAdmin)
admin.site.register(WorkSample, WorkSampleAdmin)
