from django import forms
from django.core.mail import EmailMessage
from django.template import Context, Template

from project.models import WorkSample, WorkSampleTemplate


class BulkCreateSendForm(forms.Form):
    worksample_template = forms.ModelChoiceField(
        queryset=WorkSampleTemplate.objects.all(),
    )
    applicant_names_and_emails = forms.CharField()
    from_address = forms.CharField(max_length=200)
    email_subject = forms.CharField(max_length=200)
    email_template = forms.CharField()

    def clean_applicant_names_and_emails(self):
        data = self.cleaned_data['applicant_names_and_emails']
        applicant_names_and_emails = [
            [item.strip() for item in line.split()]
            for line in data.split('\n')
        ]
        return applicant_names_and_emails

    def _build_email_messages(self):
        data = self.cleaned_data
        email_body = Template(data['email_template'])
        email_subject = Template(data['email_subject'])

        applicant_names_and_emails = data['applicant_names_and_emails']

        for first_name, last_name, applicant_email in applicant_names_and_emails:
            worksample = WorkSample.objects.create(
                template=data['worksample_template'],
                applicant_name='{} {}'.format(first_name, last_name),
                applicant_email=applicant_email,
            )
            context = Context(dict(
                APPLICANT_FIRST_NAME=first_name.title(),
                WORKSAMPLE_URL=worksample.get_absolute_url(),
            ))
            email = EmailMessage(
                from_email=data['from_address'],
                to=[applicant_email],
                subject=email_subject.render(context),
                body=email_body.render(context),
            )
            yield email

    def send_emails(self):
        messages = list(self._build_email_messages())
        for message in messages:
            pass
        # message.send()
