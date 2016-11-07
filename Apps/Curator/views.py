from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'curator/index.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)