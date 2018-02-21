import mimetypes
import logging

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string

from project.forms import BulkCreateSendForm
from project.models import WorkSample, WorkSampleTemplate


__all__ = [
    'index',
    'start_worksample',
    'complete_worksample',
    'download_worksample_submission',
    'bulk_send_worksample_email',
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
        email_worksample(request, worksample)
    return redirect('worksample', uuid=uuid)


def save_worksample(worksample, submission):
    worksample.submission = submission.read()
    worksample.submission_file_name = submission.name
    worksample.finish_time = timezone.now()
    worksample.save()


def email_worksample(request, worksample):
    if not settings.SENDGRID_API_KEY:
        # On production, this setting is required. settings.py already handles that.
        # On local dev, this setting is optional
        logger.warning(
            'SENDGRID_API_KEY was not set in the environment. No emails will be sent'
        )
        return
    subject = '{role} work sample submission from {name} ({uuid})'.format(
        role=worksample.template.description,
        name=worksample.applicant_name,
        uuid=worksample.uuid,
    )

    recipients = [
        email.strip()
        for email in worksample.template.email_recipients.split(',')
    ]

    context = dict(
        request=request,
        worksample=worksample,
    )
    message = render_to_string('submission_email.txt', context)

    email = EmailMessage(
        from_email=settings.SERVER_EMAIL,
        to=recipients,
        subject=subject,
        body=message,
    )
    email.attach(
        filename=worksample.submission_file_name,
        content=worksample.submission,
    )
    email.send()


@staff_member_required
def download_worksample_submission(request, uuid):
    worksample = get_object_or_404(WorkSample, uuid=uuid)
    content_type, encoding = mimetypes.guess_type(worksample.submission_file_name)
    response = HttpResponse(worksample.submission, content_type=content_type)
    disposition = 'attachment; filename="{}"'.format(
        worksample.submission_file_name,
    )
    response['Content-Disposition'] = disposition
    response['Content-Length'] = len(worksample.submission)
    return response


@staff_member_required
def bulk_send_worksample_email(request):
    if request.method != 'POST':
        template = 'bulk_send_worksample_email.haml'
        templates = list(WorkSampleTemplate.objects.values_list('pk', 'description'))
        context = dict(
            worksample_templates=templates,
        )
        return render(request, template, context)

    form = BulkCreateSendForm(request.POST)
    if form.is_valid():
        form.send_emails()
    return redirect('bulk_create_worksample')
