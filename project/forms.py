from django import forms
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils.html import strip_tags

from project.models import WorkSample, WorkSampleTemplate


class BulkCreateSendForm(forms.Form):
    worksample_template = forms.ModelChoiceField(
        queryset=WorkSampleTemplate.objects.all(),
    )
    applicant_names_and_emails = forms.CharField()
    from_address = forms.CharField(max_length=200)
    email_subject = forms.CharField(max_length=200)
    email_template = forms.CharField()
    should_send_emails = forms.BooleanField(required=False)

    def clean_applicant_names_and_emails(self):
        data = self.cleaned_data['applicant_names_and_emails']
        applicant_names_and_emails = [
            [item.strip() for item in line.split()]
            for line in data.split('\n')
        ]
        return applicant_names_and_emails

    def _build_email_messages(self, request):
        data = self.cleaned_data
        template_body = Template(data['email_template'])
        template_subject = Template(data['email_subject'])

        applicant_names_and_emails = data['applicant_names_and_emails']

        from_address = data['from_address']
        if request.user.first_name:
            from_address = '{} {} <{}>'.format(
                request.user.first_name,
                request.user.last_name,
                from_address,
            )

        # if we're not actually sending the email, don't save the
        # worksample instance to the DB
        worksample_create_func = WorkSample
        if self.cleaned_data['should_send_emails']:
            worksample_create_func = WorkSample.objects.create

        for first_name, last_name, applicant_email in applicant_names_and_emails:
            first_name = first_name.title()
            last_name = last_name.title()

            worksample = worksample_create_func(
                template=data['worksample_template'],
                applicant_name='{} {}'.format(first_name, last_name),
                applicant_email=applicant_email,
                created_by_user=request.user,
            )
            path = worksample.get_absolute_url()
            worksample_url = request.build_absolute_uri(path)
            context = Context(dict(
                APPLICANT_FIRST_NAME=first_name.title(),
                WORKSAMPLE_URL=worksample_url,
            ))
            body = template_body.render(context)
            body_no_html = strip_tags(body)

            applicant_email = '{} {} <{}>'.format(first_name, last_name, applicant_email)
            email = EmailMultiAlternatives(
                from_email=from_address,
                to=[applicant_email],
                subject=template_subject.render(context),
                body=body_no_html,
            )
            if body_no_html != body:
                email.attach_alternative(body, 'text/html')
            yield email

    def send_emails(self, request):
        messages = list(self._build_email_messages(request))
        results = []
        should_send_emails = self.cleaned_data['should_send_emails']
        for message in messages:
            email_was_sent = False
            if should_send_emails:
                email_was_sent = message.send()
            results.append((email_was_sent, message))
        return results
