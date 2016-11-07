from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'curator/index.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class OpinionsView(TemplateView):
    template_name = 'curator/opinions.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class OpinionsView(TemplateView):
    template_name = 'curator/opinions.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class NewRoomsView(TemplateView):
    template_name = 'curator/new-rooms.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class RoomsView(TemplateView):
    template_name = 'curator/rooms.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class ResourcesView(TemplateView):
    template_name = 'curator/resources.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)