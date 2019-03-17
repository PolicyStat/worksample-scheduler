import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel


class WorkSampleTemplate(TimeStampedModel):
    is_active = models.BooleanField(default=True)

    description = models.CharField(
        max_length=255,
        help_text='What role is this for?',
    )
    welcome_message = models.TextField(
        help_text='The first page that is displayed. Use Markdown.'
    )
    instructions = models.TextField(
        help_text='The work sample instructions. Use Markdown.'
    )
    final_message = models.TextField(
        help_text='The page that appears after submitting. Use Markdown.'
    )
    allowed_minutes = models.IntegerField()
    email_recipients = models.TextField(
        help_text='Multiple email addresses can be entered. Separate addresses using a comma',
    )

    created_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.description


class WorkSample(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(WorkSampleTemplate, on_delete=models.PROTECT)
    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    submission = models.BinaryField(null=True, blank=True)
    submission_file_name = models.CharField(max_length=255, null=True, blank=True)
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.CharField(max_length=255, null=True, blank=True)
    created_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return '{name} <{email}> ({uuid})'.format(
            name=self.applicant_name,
            email=self.applicant_email,
            uuid=self.uuid,
        )

    def get_absolute_url(self):
        return reverse('worksample', kwargs=dict(uuid=self.uuid))

    def get_time_spent_in_minutes(self):
        if self.finish_time is None:
            return
        delta = self.finish_time - self.start_time
        return delta.total_seconds() / 60

    def get_time_difference_from_allowed_time(self):
        time_spent = self.get_time_spent_in_minutes()
        return abs(time_spent - self.template.allowed_minutes)

    def expected_finish_time(self):
        return self.start_time + timedelta(minutes=self.template.allowed_minutes)
