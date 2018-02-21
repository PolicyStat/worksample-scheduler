from django import forms
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils.html import linebreaks, strip_tags

from project.models import WorkSample, WorkSampleTemplate


class BulkCreateSendForm(forms.Form):
    worksample_template = forms.ModelChoiceField(
        queryset=WorkSampleTemplate.objects.all(),
    )
    applicant_names_and_emails = forms.CharField()
    from_address = forms.CharField(max_length=200)
    email_subject = forms.CharField(max_length=200)
    email_template = forms.CharField()
    show_preview = forms.BooleanField()

    def clean_applicant_names_and_emails(self):
        data = self.cleaned_data['applicant_names_and_emails']
        applicant_names_and_emails = [
            [item.strip() for item in line.split()]
            for line in data.split('\n')
        ]
        return applicant_names_and_emails

    def clean_show_preview(self):
        if self.cleaned_data['show_preview'] == 'preview':
            return True
        return False

    def _build_email_messages(self, request):
        data = self.cleaned_data
        template_body = Template(data['email_template'])
        template_subject = Template(data['email_subject'])

        applicant_names_and_emails = data['applicant_names_and_emails']

        for first_name, last_name, applicant_email in applicant_names_and_emails:
            worksample = WorkSample.objects.create(
                template=data['worksample_template'],
                applicant_name='{} {}'.format(first_name, last_name),
                applicant_email=applicant_email,
            )
            path = worksample.get_absolute_url()
            worksample_url = request.build_absolute_uri(path)
            context = Context(dict(
                APPLICANT_FIRST_NAME=first_name.title(),
                WORKSAMPLE_URL=worksample_url,
            ))
            body = template_body.render(context)
            body_no_html = strip_tags(body)
            email = EmailMultiAlternatives(
                from_email=data['from_address'],
                to=[applicant_email],
                subject=template_subject.render(context),
                body=body_no_html,
            )
            if body_no_html != body:
                body_with_converted_linebreaks = linebreaks(body)
                email.attach_alternative(body_with_converted_linebreaks, 'text/html')
            yield email

    def send_emails(self, request, dry_run=False):
        messages = list(self._build_email_messages(request))
        results = []
        result = dry_run
        for message in messages:
            if not dry_run:
                result = message.send()
            results.append((result, message))
        return results
