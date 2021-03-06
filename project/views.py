import mimetypes
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string

from ckeditor.widgets import CKEditorWidget

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
    context = dict(
        worksample=obj,
    )
    if not obj.start_time:
        template = 'welcome.haml'
    elif obj.finish_time:
        template = 'done.haml'
    elif not can_complete_worksample(obj):
        template = 'out_of_time.haml'
    else:
        template = 'instructions.haml'
    return render(request, template, context)


def start_worksample(request, uuid):
    worksample = get_object_or_404(WorkSample, uuid=uuid)
    if request.method == 'POST' and worksample.start_time is None:
        worksample.start_time = timezone.now()
        worksample.save()
    return redirect('worksample', uuid=uuid)


def can_complete_worksample(worksample):
    if worksample.start_time is None:
        return False
    submission_buffer = timedelta(minutes=2)
    max_finish_time = worksample.expected_finish_time() + submission_buffer
    now = timezone.now()
    if now > max_finish_time:
        return False
    return worksample.finish_time is None


def complete_worksample(request, uuid):
    worksample = get_object_or_404(WorkSample, uuid=uuid)
    if can_complete_worksample(worksample):
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

    worksample_path = reverse('admin:worksample_download', kwargs=dict(uuid=worksample.uuid))
    worksample_url = request.build_absolute_uri(worksample_path)

    context = dict(
        request=request,
        worksample=worksample,
        worksample_url=worksample_url,
    )
    message = render_to_string('submission_email.txt', context)

    email = EmailMessage(
        from_email=settings.SERVER_EMAIL,
        to=recipients,
        subject=subject,
        body=message,
    )
    email.send()


@staff_member_required
def bulk_send_worksample_email(request):
    if request.method != 'POST':
        editor = CKEditorWidget(
            config_name='admin',
            attrs={
                'id': 'email_template_editor',
            }
        )
        template = 'bulk_send_worksample_email.haml'
        templates = list(WorkSampleTemplate.objects.filter(
            is_active=True,
        ).values_list('pk', 'description'))
        emails = request.session.pop('emails', None)

        form = request.session.get('bulk_create_form', {})
        editor_html = editor.render('email_template', form.get('email_template'))

        context = dict(
            worksample_templates=templates,
            form=form,
            emails=emails,
            editor_html=editor_html,
        )
        return render(request, template, context)

    request.session['bulk_create_form'] = request.POST
    form = BulkCreateSendForm(request.POST)
    if form.is_valid():
        emails = form.send_emails(request)
        session_emails = []
        for email_sent, email in emails:
            body = email.body
            if email.alternatives:
                body = email.alternatives[0][0]
            session_email = dict(
                was_sent=email_sent,
                subject=email.subject,
                to=email.to[0],
                from_address=email.from_email,
                body=body,
            )
            session_emails.append(session_email)
        request.session['emails'] = session_emails
    return redirect('bulk_create_worksample')
