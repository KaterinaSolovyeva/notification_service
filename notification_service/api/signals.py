import logging

from api.tasks import start_notification
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from notifications.models import Client, Message, MobileCode, Notification


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def create_update_notification_log(sender, instance, created, **kwargs):
    date = instance.date_time_start.replace(tzinfo=None)
    if created:
        logger.info(
            f'Было создано  Notification_id {instance}: {instance.__dict__ }'
        )
    else:
        logger.info(
            f'Было обновлено Notification_id {instance}: {instance.__dict__ }'
        )
    notification_id = instance.id

    start_notification.apply_async((notification_id,), eta=date)


@receiver(post_delete, sender=Notification)
def delete_notification_log(sender, instance, using, **kwargs):
    logger.info(f'Было удалено Notification_id {instance}')


@receiver(post_save, sender=Message)
def create_update_message_log(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f'Было создано  Message_id {instance}: {instance.__dict__ }'
        )
    else:
        logger.info(
            f'Было обновлено Message_id {instance}: {instance.__dict__ }'
        )


@receiver(post_delete, sender=Message)
def delete_message_log(sender, instance, using, **kwargs):
    logger.info(f'Было удалено Message_id {instance}')


@receiver(post_save, sender=Client)
def create_update_client_log(sender, instance, created, **kwargs):
    MobileCode.objects.get_or_create(mobile_code=instance.mobile_code)
    if created:
        logger.info(f'Был создан  Сlient_id {instance}: {instance.__dict__ }')
    else:
        logger.info(f'Был обновлен Сlient_id {instance}: {instance.__dict__ }')


@receiver(post_delete, sender=Client)
def delete_client_log(sender, instance, using, **kwargs):
    logger.info(f'Был удален Сlient_id {instance}')
