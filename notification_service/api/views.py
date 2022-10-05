from notifications.models import Client, Message, Notification
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (ClientSerializer, MessageSerializer,
                          NotificationSerializer)


class ClientViewSet(viewsets.ModelViewSet):
    """Модель обработки запроса к информации о клиенте."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    pagination_class = LimitOffsetPagination


class NotificationViewSet(viewsets.ModelViewSet):
    """Модель обработки запросов к уведомлениям."""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    pagination_class = LimitOffsetPagination


class NotificationMessageViewSet(viewsets.ModelViewSet):
    """Модель обработки запросов к сообщениям по конкретной рассылке."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        notification_id = self.kwargs.get('notification_id')
        new_queryset = Message.objects.filter(notification_id=notification_id)
        return new_queryset

    def perform_create(self, serializer):
        notification_id = self.kwargs.get('notification_id')
        serializer.save(notification_id=notification_id)


class MessageViewSet(viewsets.ModelViewSet):
    """Модель обработки запросов сообщениям"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination
