import copy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.forms import ImageForm, TemplateForm, ModelForm, MusicForm
from Apps.Curator.models import ExternalMusic, ExternalImage, ExternalModel, ExternalTemplate


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
    selector = {'header': {'display': 'Models, Music, Images, etc:',
                           'selected': 'selected'},
                'options': [{'value': 'music', 'display': 'Music', 'selected': ''},
                            {'value': 'images', 'display': 'Images', 'selected': ''},
                            {'value': 'models', 'display': 'Models', 'selected': ''}]}

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
            elif specific_resource == 'models':
                specific_template = 'curator/resources/resources-models.html'
                specific_selector['options'][2]['selected'] = 'selected'

        if new in ['1']:
            url = '/curator/new-resources?resource='+specific_resource
            return redirect(url)

        return render(request, specific_template, specific_selector)


class NewResourcesView(TemplateView):
    template_name = 'curator/new-resource.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        parameters = {}
        form_type = request.GET.get('resource', None)
        if form_type:
            if form_type == 'music':
                form = MusicForm()
            elif form_type == 'images':
                form = ImageForm()
            elif form_type == 'models':
                form = ModelForm()
            else:
                form = TemplateForm()
            parameters = {'form': form}

        return render(request, self.template_name, parameters)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        request_form = ImageForm(request.POST, request.FILES)
        if request_form.is_valid():
            request_form.save()
        return redirect('/curator/resources')


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)
