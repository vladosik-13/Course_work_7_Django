from django import forms
from .models import Client, Message, Mailing

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'name', 'comment']

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите Email'
        })

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите Ф.И.О.'
        })

        self.fields['comment'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите комментарий'
        })


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'text_message']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        self.fields['subject'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Тема сообщения'
        })

        self.fields['text_message'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Текст сообщения'
        })


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'status', 'message', 'clients']

    def __init__(self, *args, **kwargs):
        super(MailingForm, self).__init__(*args, **kwargs)

        self.fields['start_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Дата начала рассылки'
        })

        self.fields['end_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Дата окончания рассылки'
        })

        self.fields['status'].widget.attrs.update({
            'class': 'form-control'})

        self.fields['message'].widget.attrs.update({
            'class': 'form-control'})

        self.fields['clients'].widget.attrs.update({
            'class': 'form-control'})
