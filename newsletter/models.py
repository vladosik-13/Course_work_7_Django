from django.db import models


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=200, verbose_name="ФИО")
    comment = models.TextField(max_length=500, verbose_name="Комментарий")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    text_message = models.TextField(verbose_name='Тело письма')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'