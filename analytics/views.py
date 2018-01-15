from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg, Count
from django.utils import timezone

import datetime
from orders.models import Order


class SalesView(TemplateView, LoginRequiredMixin):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "403.html")
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        two_weeks_ago = timezone.now() - datetime.timedelta(days=14)
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        qs = Order.objects.all().by_weeks_range(weeks_ago=10, number_of_weeks=10)
        context['orders'] = qs
        context['today'] = qs.by_range(start_date=timezone.now().date())
        context['this_week'] = Order.objects.all().by_weeks_range(weeks_ago=1, number_of_weeks=1).get_data_breakdown()
        context['last_four_weeks'] = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=4).get_data_breakdown()
        return context
