import copy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.forms import ImageForm, TemplateForm, ModelForm, MusicForm


POSSIBLE_RESOURCE = {
    'Music': {
        'name': 'Music', 'form': MusicForm, 'template': 'curator/resources/resources-music.html'
    },
    'Image': {
        'name': 'Image', 'form': ImageForm, 'template': 'curator/resources/resources-images.html'
    },
    'Model': {
        'name': 'Model', 'form': ModelForm, 'template': 'curator/resources/resources-models.html'
    },
}


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
                           'selected': 'selected'}, 'options': []}
    for resource in POSSIBLE_RESOURCE:
        resource = POSSIBLE_RESOURCE[resource]
        local_dict = {'value': resource['name'],
                      'display': resource['name'],
                      'selected': ''}
        selector['options'].append(local_dict)

    def selector_current(self, specific_resource):

        specific_selector = copy.deepcopy(self.selector)
        specific_template = self.template_name

        if specific_resource:
            specific_selector['header']['selected'] = ''
            specific_template = POSSIBLE_RESOURCE.get(specific_resource, None)

            if specific_template is not None:
                specific_template = specific_template['template']
                for option in specific_selector['options']:
                    if option['value'] == specific_resource:
                        option['selected'] = 'selected'
        return specific_selector, specific_template

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        specific_resource = request.GET.get('resource', None)
        specific_selector, specific_template = self.selector_current(specific_resource)

        success = request.GET.get('success', None)
        if success is not None and success == 'true':
            specific_selector['success'] = True

        return render(request, specific_template, specific_selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):

        specific_resource = request.POST.get('resource', None)
        new = request.POST.get('new-resource', None)
        specific_selector, specific_template = self.selector_current(specific_resource)

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
            form = POSSIBLE_RESOURCE.get(form_type, None)

            if form is not None:
                form = form['form']()
            else:
                form = TemplateForm()

            parameters = {'form': form, 'resource': form_type}

        return render(request, self.template_name, parameters)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        request_form = TemplateForm(request.POST, request.FILES)
        args = {}

        form_type = request.GET.get('resource', None)
        if form_type:
            args['resource'] = form_type
            form_type = POSSIBLE_RESOURCE.get(form_type, None)

            if form_type is not None:
                request_form = form_type['form'](request.POST, request.FILES)

        if request_form.is_valid():
            request_form.save()
            return redirect('/curator/resources?success=true&resource='+args['resource'])

        args['form'] = request_form

        return render(request, self.template_name, args)


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)
