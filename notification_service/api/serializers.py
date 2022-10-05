from notifications.models import Client, Message, MobileCode, Notification, Tag
from rest_framework import serializers

from notification_service.settings import DATE_FORMAT, STATUSES


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name']
        model = Tag


class MobileCodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['mobile_code']
        model = MobileCode


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Message


class ClientSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True, many=True)

    class Meta:
        fields = ['id', 'telephone', 'mobile_code', 'tag', 'timezone']
        model = Client
        depth = 1

    def create(self, validated_data):
        client = Client.objects.create(**validated_data)
        tags_data = self.initial_data.get('tag')
        if tags_data:
            for tag in tags_data:
                Tag.objects.get_or_create(
                    name=tag.strip(),
                )
                client.tag.add(Tag.objects.get(name=tag.strip()))
        client.save()
        return client

    def update(self, instance, validated_data):
        instance.telephone = validated_data.get(
            'telephone', instance.telephone
        )
        instance.timezone = validated_data.get('timezone', instance.timezone)
        tags_data = self.initial_data.get('tag')
        if tags_data is not None:
            instance.tag.clear()
            for tag in tags_data:
                Tag.objects.get_or_create(
                    name=tag.strip(),
                )
                instance.tag.add(Tag.objects.get(name=tag.strip()))
        instance.save()
        return instance

    def validate(self, data):
        tags = self.initial_data.get('tag')
        if type(tags) is not list:
            raise serializers.ValidationError(
                'Тег должен быть передан списком.'
            )
        return data


class NotificationSerializer(serializers.ModelSerializer):
    date_time_start = serializers.DateTimeField(format=DATE_FORMAT)
    date_time_stop = serializers.DateTimeField(format=DATE_FORMAT)
    number_of_messages = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id', 'date_time_start', 'text',
            'date_time_stop', 'number_of_messages'
        ]
        model = Notification

    def get_number_of_messages(self, obj):
        number_of_messages = {}
        for status in STATUSES:
            status = status[0]
            number = obj.messages.filter(status=status).count()
            number_of_messages[status] = number
        return number_of_messages

    def create(self, validated_data):
        notification = Notification.objects.create(**validated_data)
        tags_data = self.initial_data.get('tag')
        mobile_code_data = self.initial_data.get('mobile_code')
        for tag in tags_data:
            notification.tag.add(Tag.objects.get(name=tag.strip()))
        for mobile_code in mobile_code_data:
            notification.mobile_code.add(
                MobileCode.objects.get(mobile_code=mobile_code)
            )
        notification.save()
        return notification

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.date_time_start = validated_data.get(
            'date_time_start', instance.date_time_start
        )
        instance.date_time_stop = validated_data.get(
            'date_time_stop', instance.date_time_stop
        )
        tags_data = self.initial_data.get('tag')
        mobile_code_data = self.initial_data.get('mobile_code')
        if tags_data is not None:
            instance.tag.clear()
            for tag in tags_data:
                instance.tag.add(Tag.objects.get(name=tag.strip()))
        if mobile_code_data is not None:
            instance.mobile_code.clear()
            for mobile_code in mobile_code_data:
                instance.mobile_code.add(
                    MobileCode.objects.get(mobile_code=mobile_code)
                )
        instance.save()
        return instance

    def validate(self, data):
        tags = self.initial_data.get('tag')
        mobile_codes = self.initial_data.get('mobile_code')
        if type(tags) is list:
            for tag in tags:
                if not Tag.objects.filter(name=tag.strip()).exists():
                    raise serializers.ValidationError(
                        f'Тега {tag} в базе нет.'
                    )
        else:
            raise serializers.ValidationError(
                'Тег должен быть передан списком.'
            )
        if type(mobile_codes) is list:
            for mobile_code in mobile_codes:
                if not MobileCode.objects.filter(
                    mobile_code=mobile_code
                ).exists():
                    raise serializers.ValidationError(
                        f'Кода мобильного оператора {mobile_code} в базе нет.'
                    )
        else:
            raise serializers.ValidationError(
                'Код мобильного оператора должен быть списком из чисел.'
            )
        return data
