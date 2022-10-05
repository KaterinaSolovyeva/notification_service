from django.utils.timezone import now
from notifications.models import Client, Notification
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

NOTIFICATION_TEXT = 'Текст тестового уведомления'
TAG = 'тестовый тег'
MOBILE_CODE = 934
CLIENT_PHONE = '79345555555'


class TestView(APITestCase):
    def setUp(self):
        self.guest_client = APIClient()

    def test_client(self):
        client_count = Client.objects.all().count()
        client_data = {"telephone": CLIENT_PHONE, "tag": [TAG]}
        response = self.guest_client.post(
            '/api/v1/clients/', client_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.all().count(), client_count + 1)
        self.assertEqual(response.data['telephone'], CLIENT_PHONE)
        self.assertIsInstance(response.data['telephone'], str)

    def test_notification(self):
        self.test_client()
        notification_count = Notification.objects.all().count()
        notification_data = {
            "date_time_start": str(now()), "date_time_stop": str(now()),
            "text": NOTIFICATION_TEXT, "tag": [TAG],
            "mobile_code": [MOBILE_CODE]
        }
        response = self.guest_client.post(
            '/api/v1/notifications/', notification_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Notification.objects.all().count(), notification_count + 1
        )
        self.assertEqual(response.data['text'], NOTIFICATION_TEXT)
        self.assertIsInstance(response.data['text'], str)

    def test_stat(self):
        self.test_notification()
        response = self.guest_client.get('/api/v1/notifications/')
        self.assertIsInstance(
            response.data['results'][0]['number_of_messages'], dict
        )
        response = self.guest_client.get('/api/v1/notifications/1/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
