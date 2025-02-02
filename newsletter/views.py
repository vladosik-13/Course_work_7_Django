from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

# Проверка владельца рассылки
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.has_perm('newsletter.view_all_mailings')

# Главная страница
class HomeView(LoginRequiredMixin, ListView):
    template_name = 'newsletter/home.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            context['total_mailings'] = Mailing.objects.count()
            context['active_mailings'] = Mailing.objects.filter(status='STARTED').count()
            context['unique_clients'] = Client.objects.count()
        else:
            context['total_mailings'] = Mailing.objects.filter(owner=self.request.user).count()
            context['active_mailings'] = Mailing.objects.filter(owner=self.request.user, status='STARTED').count()
            context['unique_clients'] = Client.objects.filter(mailings__owner=self.request.user).distinct().count()
        return context

# Список рассылок
@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'newsletter/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

# Детальное представление рассылки
class MailingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Mailing
    template_name = 'newsletter/mailing_detail.html'
    context_object_name = 'mailing'

# Создание рассылки
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'newsletter/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Добавить рассылку'
        return context

# Редактирование рассылки
class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'newsletter/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать рассылку'
        return context

# Удаление рассылки
class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'newsletter/confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

# Отправка рассылки
class MailingSendView(LoginRequiredMixin, OwnerRequiredMixin, FormView):
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

# Список клиентов
@method_decorator(cache_page(60 * 15), name='dispatch')
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'newsletter/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            return Client.objects.all()
        return Client.objects.filter(mailings__owner=self.request.user).distinct()

# Детальное представление клиента
class ClientDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Client
    template_name = 'newsletter/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self):
        queryset = cache.get('client_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('client_queryset', queryset, 60 * 15)
        return queryset

# Создание клиента
class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'newsletter/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Добавить клиента'
        return context

# Редактирование клиента
class ClientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'newsletter/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать клиента'
        return context

# Удаление клиента
class ClientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Client
    template_name = 'newsletter/confirm_delete.html'
    success_url = reverse_lazy('client_list')

# Список сообщений
@method_decorator(cache_page(60 * 15), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'newsletter/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            return Message.objects.all()
        return Message.objects.filter(mailings__owner=self.request.user).distinct()

# Детальное представление сообщения
@method_decorator(cache_page(60 * 15), name='dispatch')
class MessageDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Message
    template_name = 'newsletter/message_detail.html'
    context_object_name = 'message'

# Создание сообщения
class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'newsletter/message_form.html'
    success_url = reverse_lazy('message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Добавить сообщение'
        return context

# Редактирование сообщения
class MessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'newsletter/message_form.html'
    success_url = reverse_lazy('message_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать сообщение'
        return context

# Удаление сообщения
class MessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Message
    template_name = 'newsletter/confirm_delete.html'
    success_url = reverse_lazy('message_list')

# Статистика и отчеты
class MailingReportView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'newsletter/mailing_report.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempts = self.get_queryset()
        context['total_attempts'] = attempts.count()
        context['successful_attempts'] = attempts.filter(success=True).count()
        context['failed_attempts'] = attempts.filter(success=False).count()
        return context


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'newsletter/mailing_attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        if self.request.user.has_perm('newsletter.view_all_mailings'):
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)