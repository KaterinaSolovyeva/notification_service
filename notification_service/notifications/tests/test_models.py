from django.utils.timezone import now
from rest_framework.test import APITestCase

from ..models import Client, Message, MobileCode, Notification, Tag

NOTIFICATION_TEXT = 'Текст тестового уведомления'
TAG = 'тестовый тег для модели'
MOBILE_CODE = 935
CLIENT_PHONE = '79351111111'


class TestModel(APITestCase):

    def test_creates_client_with_tag(self):
        tag = Tag.objects.create(name=TAG)
        client = Client.objects.create(telephone=CLIENT_PHONE)
        client.tag.add(tag)
        self.assertIsInstance(client, Client)
        self.assertEqual(client.telephone, CLIENT_PHONE)
        self.assertEqual(client.tag.values_list('name', flat=True)[0], TAG)

    def test_creates_notification(self):
        tag = Tag.objects.create(name=TAG)
        mobile_code = MobileCode.objects.create(mobile_code=MOBILE_CODE)
        notification = Notification.objects.create(
            date_time_start=now(), date_time_stop=now(),
            text=NOTIFICATION_TEXT
        )
        notification.tag.add(tag)
        notification.mobile_code.add(mobile_code)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.text, NOTIFICATION_TEXT)
        self.assertEqual(
            notification.tag.values_list('name', flat=True)[0], TAG
        )

    def test_creates_message(self):
        self.test_creates_notification()
        notification = Notification.objects.first()
        message = Message.objects.create(notification_id=notification.id)
        self.assertIsInstance(message, Message)
