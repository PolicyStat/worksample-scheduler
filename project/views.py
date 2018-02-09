import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect

from project.models import WorkSample


__all__ = [
    'index',
    'start_worksample',
    'complete_worksample',
]

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("There's nothing to see here")


def worksample(request, uuid):
    obj = get_object_or_404(WorkSample, uuid=uuid)
    template = 'welcome.haml'
    if obj.finish_time:
        template = 'done.haml'
    elif obj.start_time:
        template = 'instructions.haml'
    context = dict(
        worksample=obj,
    )
    return render(request, template, context)


def can_start_worksample(request, worksample):
    if request.method != 'POST':
        return False
    return worksample.start_time is None


def start_worksample(request, uuid):
    worksample = get_object_or_404(WorkSample, uuid=uuid)
    if can_start_worksample(request, worksample):
        worksample.start_time = timezone.now()
        worksample.save()
    return redirect('worksample', uuid=uuid)


def can_complete_worksample(request, worksample):
    if request.method != 'POST':
        return False
    if worksample.start_time is None:
        return False
    return worksample.finish_time is None


def complete_worksample(request, uuid):
    worksample = get_object_or_404(WorkSample, uuid=uuid)
    if can_complete_worksample(request, worksample):
        submission = request.FILES['submission']
        save_worksample(worksample, submission)
        email_worksample(worksample)
    return redirect('worksample', uuid=uuid)


def save_worksample(worksample, submission):
    worksample.submission = submission.read()
    worksample.submission_file_name = submission.name
    worksample.finish_time = timezone.now()
    worksample.save()


def email_worksample(worksample):
    if not settings.SENDGRID_API_KEY:
        # On production, this setting is required. settings.py already handles that.
        # On local dev, this setting is optional
        logger.warning(
            'SENDGRID_API_KEY was not set in the environment. No emails will be sent'
        )
        return
    subject = 'WorkSample submission from {}'.format(
        worksample.applicant_name,
    )

    recipients = [
        email.strip()
        for email in worksample.template.email_recipients.split(',')
    ]

    message = 'The message'

    email = EmailMessage(
        from_email='noreply@policystat.com',
        to=recipients,
        subject=subject,
        body=message,
    )
    email.attach(
        filename=worksample.submission_file_name,
        content=worksample.submission,
    )
    email.send()
