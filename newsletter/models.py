from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=200, verbose_name="ФИО")
    comment = models.TextField(max_length=500, verbose_name="Комментарий", blank=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [
            ("view_all_clients", "Просматривать всех клиентов"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    text_message = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("view_all_messages", "Просматривать все сообщения"),
        ]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Создана"),
        ("STARTED", "Запущена"),
        ("COMPLETED", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время первой отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="CREATED", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    clients = models.ManyToManyField(
        Client, related_name="mailings", verbose_name="Получатели"
    )
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Владелец",
    )

    def __str__(self):
        return f"Рассылка {self.id} - {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("view_all_mailings", "Просматривать все рассылки"),
        ]


class MailingAttempt(models.Model):
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    success = models.BooleanField(default=False, verbose_name="Успешно")
    response = models.TextField(blank=True, verbose_name="Ответ почтового сервера")

    def __str__(self):
        return f"Попытка {self.id} - {'Успешно' if self.success else 'Не успешно'}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
