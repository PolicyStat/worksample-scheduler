import uuid

from django.db import models
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel


class WorkSampleTemplate(TimeStampedModel):
    description = models.CharField(max_length=255)
    welcome_message = models.TextField()
    instructions = models.TextField()
    final_message = models.TextField()
    allowed_minutes = models.IntegerField()
    email_recipients = models.TextField()

    def __str__(self):
        return self.description


class WorkSample(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(WorkSampleTemplate, on_delete=models.PROTECT)
    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    submission = models.BinaryField(null=True, blank=True)
    submission_file_name = models.CharField(max_length=255, null=True, blank=True)
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.CharField(max_length=255, null=True, blank=True)

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
