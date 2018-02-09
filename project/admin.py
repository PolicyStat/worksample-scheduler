from django.contrib import admin
from django.utils.html import format_html

from project.models import WorkSampleTemplate, WorkSample


class WorkSampleTemplateAdmin(admin.ModelAdmin):
    list_display = ('description', 'allowed_minutes', 'email_recipients')


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
    )

    def access_url(self, obj):
        path = obj.get_absolute_url()
        return format_html('<a href="{path}">{path}</a>'.format(path=path))

    def minutes(self, obj):
        if obj.finish_time is None:
            return ''

        delta = obj.finish_time - obj.start_time
        delta_minutes = delta.total_seconds() / 60
        return '{:.4}'.format(delta_minutes)


admin.site.register(WorkSampleTemplate, WorkSampleTemplateAdmin)
admin.site.register(WorkSample, WorkSampleAdmin)
