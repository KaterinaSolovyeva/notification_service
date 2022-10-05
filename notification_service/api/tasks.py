from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from notifications.models import Client, Message, Notification

from notification_service.settings import EMAIL_HOST_USER, STATUSES, TOKEN, URL

logger = get_task_logger(__name__)


@shared_task
def start_notification(notification_id):
    now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
    notification = Notification.objects.filter(
        Q(
            id=notification_id
        ) & Q(date_time_start__lte=now) & Q(date_time_stop__gt=now)
    ).first()
    try:
        mobile_codes = notification.mobile_code.values_list(
            'mobile_code', flat=True
        )
        tags = notification.tag.values_list('name', flat=True)
    except AttributeError:
        pass
    else:
        if notification:
            clients = Client.objects.filter(
                Q(tag__name__in=tags) | Q(mobile_code__in=mobile_codes)
            )
            for client in clients.values():
                if not Message.objects.filter(
                    Q(
                        notification__id=notification_id
                    ) & Q(clients__id=client['id'])
                ).exists():
                    message = Message(
                        notification=notification,
                        status=STATUSES[0][0]
                    )
                    message.save()
                    message.clients.add(client['id'])
                    message.save()
                    logger.info(f"Message_id: {message} {STATUSES[0][1]}")
                    data = {
                        'id': message.id,
                        'phone': client['telephone'],
                        'text': notification.text
                    }
                    send_message.apply_async(
                        (data, notification.id, client['timezone']),
                        countdown=1
                    )


@shared_task(bind=True, retry_backoff=True, max_retries=24)
def send_message(self, data, notification_id, client_timezone):
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    timezone.activate(ZoneInfo(client_timezone))
    client_tz = timezone.get_current_timezone()
    client_now_hour = datetime.now().astimezone(client_tz).hour
    if Notification.objects.filter(
        Q(id=notification_id) & Q(time_interval__contains=client_now_hour)
    ).exists():
        try:
            requests.post(
                url=URL + str(data['id']), headers=headers, json=data
            )
        except requests.exceptions.RequestException as exc:
            logger.error(
                f"Ошибка в работе внешнего сервиса Message_id: {data['id']}"
            )
            raise self.retry(exc=exc)
        else:
            Message.objects.filter(id=data['id']).update(status=STATUSES[1][0])
            logger.info(f"Message_id: {data['id']} {STATUSES[1][1]}")
    else:
        logger.info(
            f"Отправка сообщения Message_id: {data['id']} отложена на час"
        )
        self.retry(countdown=60*60)


@shared_task
def schedule_mail():
    message = str(Message.objects.values().order_by('notification__id'))
    mail = send_mail(
        'Subject here',
        message,
        EMAIL_HOST_USER,
        [EMAIL_HOST_USER],
        fail_silently=False,
    )
    if mail:
        logger.info("Статистика отправлена на e-mail")
    else:
        logger.info("Статистика не отправлена")
