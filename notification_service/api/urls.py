from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ClientViewSet, MessageViewSet, NotificationMessageViewSet,
                    NotificationViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'notifications/(?P<notification_id>\d+)/messages',
    NotificationMessageViewSet,
    basename='messages'
)
router_v1.register(
    'notifications', NotificationViewSet, basename='notification'
)
router_v1.register('clients', ClientViewSet, basename='client')
router_v1.register('messages', MessageViewSet, basename='message')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
