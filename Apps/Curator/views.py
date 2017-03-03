import copy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'curator/index.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class OpinionsView(TemplateView):
    template_name = 'curator/opinions.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class OpinionsView(TemplateView):
    template_name = 'curator/opinions.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class NewRoomsView(TemplateView):
    template_name = 'curator/new-rooms.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class RoomsView(TemplateView):
    template_name = 'curator/rooms.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class ResourcesView(TemplateView):
    template_name = 'curator/resources/resources.html'
    selector = {'header': {'display': 'Objects, Music, Images, etc:',
                           'selected': 'selected'},
                'options': [{'value': 'music', 'display': 'Music', 'selected': ''},
                            {'value': 'images', 'display': 'Images', 'selected': ''},
                            {'value': 'objects', 'display': 'Objects', 'selected': ''}]}

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name, self.selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):

        specific_resource = request.POST.get('resource', None)
        new = request.POST.get('new-resource', None)

        specific_template = self.template_name
        specific_selector = copy.deepcopy(self.selector)

        if specific_resource:
            specific_selector['header']['selected'] = ''
            if specific_resource == 'music':
                specific_template = 'curator/resources/resources-music.html'
                specific_selector['options'][0]['selected'] = 'selected'
            elif specific_resource == 'images':
                specific_template = 'curator/resources/resources-images.html'
                specific_selector['options'][1]['selected'] = 'selected'
            elif specific_resource == 'objects':
                specific_template = 'curator/resources/resources-objects.html'
                specific_selector['options'][2]['selected'] = 'selected'

        if new in ['1']:
            url = '/curator/new-resources'
            return redirect(url)

        return render(request, specific_template, specific_selector)


class NewResourcesView(TemplateView):
    template_name = 'curator/new-resource.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)
