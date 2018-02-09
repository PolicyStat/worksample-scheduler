import base64
import os
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail, Attachment

from project.models import WorkSample


__all__ = [
    'index',
    'start_worksample',
    'complete_worksample',
]


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
        worksample.start_time = datetime.now()
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
    worksample.finish_time = datetime.now()
    worksample.save()


def email_worksample(worksample):
    api_key = os.environ.get('SENDGRID_API_KEY')
    sg = SendGridAPIClient(apikey=api_key)
    from_email = Email('noreply@policystat.com')

    subject = 'WorkSample submission from {}'.format(
        worksample.applicant_name,
    )

    recipients = [
        email.strip()
        for email in worksample.template.email_recipients.split(',')
    ]

    to_email = Email(recipients.pop(0))
    body = 'Hello'
    content = Content('text/plain', body)
    mail = Mail(from_email, subject, to_email, content)

    for recipient in recipients:
        mail.personalizations[0].add_to(Email(recipient))

    attachment = Attachment()
    attachment.content = base64.b64encode(worksample.submission).decode('utf-8')
    attachment.filename = worksample.submission_file_name
    attachment.disposition = 'attachment'
    mail.add_attachment(attachment)

    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
