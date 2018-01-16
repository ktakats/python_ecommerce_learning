from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg, Count
from django.utils import timezone

import datetime
from orders.models import Order

class SalesAjaxView(View):

    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.is_staff:
            qs = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=5)
            if request.GET.get('type')=='week':
                days = 7
                start_date = timezone.now().today() - datetime.timedelta(days=days-1)
                datetime_list = [start_date + datetime.timedelta(days=x) for x in range(0, days)]
                labels = [x.strftime("%a") for x in datetime_list]
                salesItems = [qs.filter(updated__day=x.day, updated__month=x.month).totals_data()['total__sum'] or 0 for x in datetime_list]
                data['data'] = salesItems
                data['labels'] = labels

            if request.GET.get('type') == '4weeks':
                data['data'] = []
                data['labels'] = ["4 Weeks Ago", "3 Weeks Ago", "2 Weeks Ago", "Last Week", "This Week"]
                current = 5
                for i in range(0,5):
                    new_qs= qs.by_weeks_range(weeks_ago=current, number_of_weeks=1)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    data['data'].append(sales_total)
                    current -=1

        return JsonResponse(data)

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
        context['today'] = qs.by_range(start_date=timezone.now().date()).get_data_breakdown()
        context['this_week'] = Order.objects.all().by_weeks_range(weeks_ago=1, number_of_weeks=1).get_data_breakdown()
        context['last_four_weeks'] = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=4).get_data_breakdown()
        return context
