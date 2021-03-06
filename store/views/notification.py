from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import *

from store.views.utils import navbar_context
from django.utils.timezone import now
from ..models import Notification
from django.contrib.auth.models import User
from django.http import *

def create_notification(user: User, title: str, content: str) -> Notification:
    return Notification.objects.create(user=user, title=title, content=content)

def read_notification(notification: Notification) -> None:
    notification.status = 'Read'
    notification.save()

def read_all_notification(user: User) -> None:
    for notification in Notification.objects.filter(user=user):
        read_notification(notification)

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification/list.html'
    paginate_by = 10

    def get_queryset(self) -> List[Notification]:
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        hide_read = self.request.GET.get('hide_read', None) == 'true'
        if hide_read:
            queryset = queryset.filter(status='Unread')
        return queryset

    @navbar_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['hide_read'] = self.request.GET.get('hide_read', None) == 'true'
        return context

class ReadNotificationView(LoginRequiredMixin, View):
    def post(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        notification = Notification.objects.get(id=kwargs['pk'])
        if (request.user != notification.user):
            return HttpResponseForbidden()
        read_notification(notification)
        return HttpResponse(status=204)

class ReadAllNotificationView(LoginRequiredMixin, View):
    def post(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        read_all_notification(request.user)
        return HttpResponse(status=204)

class GetNotificationView(LoginRequiredMixin, View):
    def get(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        notification = Notification.objects.filter(user=request.user, status='Unread')
        request.user.profile.last_access = now()
        request.user.profile.save()
        return JsonResponse({'count': notification.count()})