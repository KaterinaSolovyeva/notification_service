from rest_framework.test import APIClient, APITestCase


class PagesURLTests(APITestCase):
    def setUp(self):
        self.guest_client = APIClient()

    def test_about_url_exists_at_desired_location(self):
        """
        Проверка доступности адресов:
        api/v1/notifications/
        api/v1/messages/
        api/v1/clients/
        """
        response = self.guest_client.get('/api/v1/notifications/')
        self.assertEqual(response.status_code, 200)
        response = self.guest_client.get('/api/v1/messages/')
        self.assertEqual(response.status_code, 200)
        response = self.guest_client.get('/api/v1/clients/')
        self.assertEqual(response.status_code, 200)
