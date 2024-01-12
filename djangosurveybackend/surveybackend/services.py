from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import TemplateDoesNotExist, render_to_string
from django.utils.html import strip_tags


class TemplateEmail:
    def __init__(
            self,
            to,
            subject,
            template,
            context,
            from_email,
            reply_to,
            **email_kwargs,
    ):
        self.to = to
        self.subject = subject
        self.template = template
        self.context = context or {}
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.reply_to = reply_to
        self.context["template"] = template
        self.html_content, self.plain_content = self.render_content()
        self.to = self.to if not isinstance(self.to, str) else [self.to]

        if self.reply_to:
            self.reply_to = (
                self.reply_to if not isinstance(self.reply_to, str) else [self.reply_to]
            )

        self.django_email = EmailMultiAlternatives(
            subject=self.subject,
            body=self.plain_content,
            from_email=self.from_email,
            to=self.to,
            reply_to=self.reply_to,
            **email_kwargs,
        )
        self.django_email.attach_alternative(self.html_content, "text/html")

    def render_content(self):
        html_content = self.render_html()

        try:
            plain_content = self.render_plain()
        except TemplateDoesNotExist:
            plain_content = strip_tags(html_content)

        return html_content, plain_content

    def add_attachment(self, attachment: str):
        self.django_email.attach_file(attachment)
        return self.django_email

    def render_plain(self):
        return render_to_string(self.get_plain_template_name(), self.context)

    def render_html(self):
        return render_to_string(self.get_html_template_name(), self.context)

    def get_plain_template_name(self):
        return f"email/{self.template}.txt"

    def get_html_template_name(self):
        return f"email/{self.template}.html"

    def send(self, **send_kwargs):
        return self.django_email.send(**send_kwargs)


class MailService:

    def __init__(
            self,
            host,
            port,
            username,
            password,
            use_tls,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls

    def send(self, to, subject, template, context, from_email, reply_to):
        with get_connection(host=self._host, port=self._port, username=self._username, password=self._password,
                            use_tls=self._use_tls) as connection:
            return TemplateEmail(to=to, subject=subject, template=template, context=context, from_email=from_email,
                                 reply_to=reply_to, connection=connection).send()
