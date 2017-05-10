from datetime import datetime

import copy
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.decorators import group_required
from Apps.Curator.models.museums import Exhibit
from Apps.Curator.models.scheduling import Exhibition
from Apps.Curator.views.opinions import get_exhibits_data


@transaction.atomic
def get_expositions():
    data = dict()
    exposition_list = list()
    expositions = Exhibition.objects.all()

    for exposition in expositions:
        exposition_template = dict()
        exposition_template['id'] = exposition.id
        exposition_template['name'] = exposition.name
        if exposition.status:
            exposition_template['status'] = 'Active'
        else:
            exposition_template['status'] = 'Inactive'
        exposition_template['start_time'] = exposition.start_date
        exposition_template['end_time'] = exposition.end_date

        exposition_list.append(exposition_template)

        data['expositions'] = exposition_list
    return data


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        expositions = get_expositions()
        return render(request, self.template_name, expositions)

    @method_decorator(group_required('Scheduling_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        change_status = request.POST.get('changing_status', None)
        exposition_id = request.POST.get('id_exposition', None)
        editing = request.POST.get('editing', None)

        if editing in ['1'] and exposition_id is not None:
            return redirect('/curator/scheduling-exposition?id=' + exposition_id)

        if change_status in ['1'] and exposition_id is not None:
            exposition = Exhibition.objects.get(id=exposition_id)
            exposition.status = not exposition.status
            exposition.save()

        expositions = get_expositions()

        return render(request, self.template_name, expositions)


class SchedulingExpositionView(TemplateView):
    template_name = 'curator/scheduling-exposition.html'
    default_selector = {'header': 'Select a Exhibit:', 'options': []}

    def get_current_selector(self):
        current_selector = copy.deepcopy(self.default_selector)
        exhibits = get_exhibits_data()
        for exhibit in exhibits:
            exhibit_template = {'value': exhibit['id'], 'display': exhibit['name']}
            current_selector['options'].append(exhibit_template)
        return current_selector

    @method_decorator(group_required('Scheduling_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        selector = self.get_current_selector()
        editing_id = request.GET.get('id', None)

        if editing_id is not None:
            exposition = Exhibition.objects.get(id=editing_id)
            selector['current_exposition'] = {'id': editing_id,
                                              'name': exposition.name,
                                              'exhibit': exposition.museum.all()[0].id,
                                              'initial': exposition.start_date,
                                              'end': exposition.end_date}
        return render(request, self.template_name, selector)

    @method_decorator(group_required('Scheduling_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        selector = self.get_current_selector()

        name = request.POST.get('name', None)
        exhibit = request.POST.get('exhibit', None)
        start_date = request.POST.get('initial', None)
        end_date = request.POST.get('end', None)

        id_editing = request.POST.get('id_exposition', None)

        try:
            if start_date is not None:
                start_date = datetime.strptime(start_date, "%d/%m/%Y")
            if end_date is not None:
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
            if end_date < start_date:
                raise ValueError('The end date is before the start date')
        except ValueError as err:
            selector['failure'] = True
            return render(request, self.template_name, selector)

        if name is not None \
                and exhibit is not None \
                and start_date is not None \
                and end_date is not None:
            if id_editing is not None:
                exposition = Exhibition.objects.get(id=id_editing)
            else:
                exposition = Exhibition()
            exposition.name = name
            exposition.start_date = start_date
            exposition.end_date = end_date

            exhibit = Exhibit.objects.get(id=exhibit)

            sid = transaction.savepoint()

            exposition.save()

            try:
                exposition.museum.add(exhibit)
                exposition.save()
                transaction.savepoint_commit(sid)
                selector['success'] = True
            except IntegrityError:
                transaction.savepoint_rollback(sid)
                selector['failure'] = True
        else:
            selector['failure'] = True
        return render(request, self.template_name, selector)