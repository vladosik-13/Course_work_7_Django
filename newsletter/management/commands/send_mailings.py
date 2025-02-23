import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from newsletter.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = "Отправляет рассылки, которые должны быть отправлены в данный момент"

    def handle(self, *args, **kwargs):
        now = datetime.datetime.now()
        mailings = Mailing.objects.filter(
            start_time__lte=now, end_time__gte=now, status="CREATED"
        )

        for mailing in mailings:
            for client in mailing.clients.all():
                try:
                    send_mail(
                        mailing.message.subject,
                        mailing.message.text_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [client.email],
                        fail_silently=False,
                    )
                    MailingAttempt.objects.create(mailing=mailing, success=True)
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing, success=False, response=str(e)
                    )

            mailing.status = "STARTED"
            mailing.save()
            self.stdout.write(self.style.SUCCESS(f"Рассылка {mailing.id} отправлена"))
