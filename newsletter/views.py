# newsletter/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm

# Главная страница
class HomeView(ListView):
    template_name = 'newsletter/home.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='STARTED').count()
        context['unique_clients'] = Client.objects.count()
        return context

# Список рассылок
class MailingListView(ListView):
    model = Mailing
    template_name = 'newsletter/mailing_list.html'
    context_object_name = 'mailings'

# Детальное представление рассылки
class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'newsletter/mailing_detail.html'
    context_object_name = 'mailing'

# Создание рассылки
class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'newsletter/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Добавить рассылку'
        return context

# Редактирование рассылки
class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'newsletter/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать рассылку'
        return context

# Удаление рассылки
class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'newsletter/confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

# Отправка рассылки
class MailingSendView(FormView):
    template_name = 'newsletter/mailing_send.html'
    success_url = reverse_lazy('mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing'] = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        for client in mailing.clients.all():
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(mailing=mailing, success=True)
            except Exception as e:
                MailingAttempt.objects.create(mailing=mailing, success=False, response=str(e))
        mailing.status = 'STARTED'
        mailing.save()
        return redirect('mailing_detail', pk=mailing.pk)