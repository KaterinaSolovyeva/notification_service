import computed_property
import pytz
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import RangeMaxValueValidator
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models.constraints import UniqueConstraint
from psycopg2.extras import NumericRange

from notification_service.settings import (END_NOTIFICATION_HOUR,
                                           START_NOTIFICATION_HOUR, STATUSES)

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


class Tag(models.Model):
    """Модель для тега."""
    name = models.CharField('Название', max_length=200, unique=True)

    class Meta:
        """Дополнительная информация по управлению моделью Tag."""
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class MobileCode(models.Model):
    """Модель для кода мобильного оператора."""
    mobile_code = models.IntegerField(
        'Код моб.оператора',
        validators=[
            MinValueValidator(
                900,
                message='Код должен быть от 900 до 999',
            ),
            MaxValueValidator(
                999,
                message='Код должен быть от 900 до 999',
            ),
        ],
        default=900
    )

    class Meta:
        """Дополнительная информация по управлению моделью MobileCode."""
        verbose_name = 'Код моб.оператора'
        verbose_name_plural = 'Коды моб.операторов'
        ordering = ('mobile_code',)

    def __str__(self):
        return str(self.mobile_code)


class Client(models.Model):
    """Модель клиента."""
    telephone = models.CharField(
        'Номер телефона',
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^7\d{10}$',
                message='Номер должен начинаться с 7 и состоять из 11 цифр.',
                code='nomatch'
            )
        ]
    )
    mobile_code = computed_property.ComputedIntegerField(
        verbose_name='Код моб.оператора',
        compute_from='get_mobile_code'
    )
    tag = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='clients',
        verbose_name='Теги',
    )
    timezone = models.CharField(
        'Часовой пояс',
        max_length=32,
        choices=TIMEZONES,
        default='UTC'
    )

    def get_mobile_code(self):
        mobile_code = str(self.telephone)[1:4]
        return mobile_code

    class Meta:
        """Дополнительная информация по управлению моделью Client."""
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('telephone',)
        constraints = [
            UniqueConstraint(
                fields=['telephone', 'mobile_code'], name='phone_unique'
            ),
        ]

    def __str__(self):
        id = str(self.id)
        return id


class Notification(models.Model):
    """Модель рассылки."""
    date_time_start = models.DateTimeField('Дата и время запуска рассылки')
    text = models.TextField('Текст')
    date_time_stop = models.DateTimeField('Дата и время окончания рассылки')
    tag = models.ManyToManyField(
        Tag,
        related_name='notifications',
        verbose_name='Теги',
    )
    mobile_code = models.ManyToManyField(
        MobileCode,
        related_name='notifications',
        verbose_name='Коды моб.операторов',
    )
    time_interval = IntegerRangeField(
        default=NumericRange(START_NOTIFICATION_HOUR, END_NOTIFICATION_HOUR),
        validators=[
            RangeMaxValueValidator(
                24,
                message='Часов в сутках не больше 24',
            )]
    )

    class Meta:
        """Дополнительная информация по управлению моделью Notification."""
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ('date_time_start',)

    def __str__(self):
        id = str(self.id)
        return id


class Message(models.Model):
    """Модель сообщения."""
    pub_date = models.DateTimeField('Дата и время отправки', auto_now_add=True)
    status = models.CharField('Статус', max_length=30, choices=STATUSES)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        verbose_name='Уведомление',
        related_name='messages'
    )
    clients = models.ManyToManyField(
        Client,
        verbose_name='Клиент',
        related_name='clients'
    )

    class Meta:
        """Дополнительная информация по управлению моделью Message."""
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-pub_date',)
