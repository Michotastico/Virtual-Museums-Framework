from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.forms import UnityMuseumForm
from Apps.Curator.models.museums import Museum
from Apps.Curator.models.scheduling import Exposition


def get_museums():
    museums_dict = {'museums': []}

    museums = Museum.objects.all()

    for museum in museums:
        expositions = Exposition.objects.filter(museum=museum).filter(status=True)
        published = True if len(expositions) > 0 else False
        museums_dict['museums'].append({'id': museum.id,
                                        'name': museum.name,
                                        'published': published,
                                        'visitors': museum.visitors})
    return museums_dict


class MuseumsView(TemplateView):
    template_name = 'curator/museums.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        museums = get_museums()
        return render(request, self.template_name, museums)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        museum_id = request.POST.get('id_museum', None)
        editing = request.POST.get('editing', None)

        if editing in ['1'] and museum_id is not None:
            return redirect('/curator/add-unity-museum?id=' + museum_id)

        expositions = get_museums()

        return render(request, self.template_name, expositions)


class AddUnityView(TemplateView):
    template_name = 'curator/unity-museum.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        form = UnityMuseumForm()
        parameters = {'form': form}

        return render(request, self.template_name, parameters)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        request_form = UnityMuseumForm(request.POST, request.FILES)
        args = {}

        if request_form.is_valid():
            request_form.save()
            args['success'] = 'success'
            request_form = UnityMuseumForm()

        args['form'] = request_form

        return render(request, self.template_name, args)
