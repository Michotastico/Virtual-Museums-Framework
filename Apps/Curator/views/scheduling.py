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
def get_exhibitions():
    data = dict()
    exhibition_list = list()
    exhibitions = Exhibition.objects.all()

    for exhibition in exhibitions:
        exhibition_template = dict()
        exhibition_template['id'] = exhibition.id
        exhibition_template['name'] = exhibition.name
        if exhibition.status:
            exhibition_template['status'] = 'Active'
        else:
            exhibition_template['status'] = 'Inactive'
        exhibition_template['start_time'] = exhibition.start_date
        exhibition_template['end_time'] = exhibition.end_date

        exhibition_list.append(exhibition_template)

    data['exhibitions'] = exhibition_list
    return data


@transaction.atomic
def delete_exhibition(exhibition):
    exhibition.delete()


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        exhibitions = get_exhibitions()
        return render(request, self.template_name, exhibitions)

    @method_decorator(group_required('Scheduling_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        change_status = request.POST.get('changing_status', None)
        exhibition_id = request.POST.get('id_exhibition', None)
        editing = request.POST.get('editing', None)
        deleting = request.POST.get('delete', None)

        if editing in ['1'] and exhibition_id is not None:
            return redirect('/curator/scheduling-exhibition?id=' + exhibition_id)

        if change_status in ['1'] and exhibition_id is not None:
            exhibition = Exhibition.objects.get(id=exhibition_id)
            exhibition.status = not exhibition.status
            exhibition.save()

        if deleting in ['1'] and exhibition_id is not None:
            exhibition = Exhibition.objects.get(id=exhibition_id)
            delete_exhibition(exhibition)

        exhibitions = get_exhibitions()

        return render(request, self.template_name, exhibitions)


class SchedulingExhibitionView(TemplateView):
    template_name = 'curator/scheduling-exhibition.html'
    default_selector = {'options': []}

    def get_current_selector(self, exclude_elements=list()):
        current_selector = copy.deepcopy(self.default_selector)
        exhibits = get_exhibits_data(exclude_elements)
        for exhibit in exhibits:
            exhibit_template = {'value': exhibit['id'], 'display': exhibit['name']}
            current_selector['options'].append(exhibit_template)
        return current_selector

    @method_decorator(group_required('Scheduling_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        selector = {}
        editing_id = request.GET.get('id', None)

        if editing_id is not None:
            exhibition = Exhibition.objects.get(id=editing_id)
            exhibits = exhibition.exhibits.all()
            exhibit_array = []
            if len(exhibits) > 0:
                for exhibit in exhibits:
                    exhibit_template = {'value': exhibit.id, 'display': exhibit.name}
                    exhibit_array.append(exhibit_template)
            selector = self.get_current_selector(exhibits)
            selector['current_exhibition'] = {'id': editing_id,
                                              'name': exhibition.name,
                                              'exhibits': exhibit_array,
                                              'initial': exhibition.start_date,
                                              'end': exhibition.end_date}
        else:
            selector = self.get_current_selector()
        return render(request, self.template_name, selector)

    @method_decorator(group_required('Scheduling_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        selector = self.get_current_selector()

        name = request.POST.get('name', None)
        exhibits = request.POST.getlist('exhibit', None)
        start_date = request.POST.get('initial', None)
        end_date = request.POST.get('end', None)

        id_editing = request.POST.get('id_exhibition', None)

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
                and exhibits is not None \
                and start_date is not None \
                and end_date is not None:
            if id_editing is not None:
                exhibition = Exhibition.objects.get(id=id_editing)
                exhibition_exhibits = exhibition.exhibits.all()
                for old_exhibit in exhibition_exhibits:
                    exhibition.exhibits.remove(old_exhibit)
            else:
                exhibition = Exhibition()
            exhibition.name = name
            exhibition.start_date = start_date
            exhibition.end_date = end_date

            exhibits_objects = list()
            for exhibit in exhibits:
                exhibits_objects.append(Exhibit.objects.get(id=exhibit))

            sid = transaction.savepoint()

            exhibition.save()

            try:
                for exhibit in exhibits_objects:
                    exhibition.exhibits.add(exhibit)
                exhibition.save()
                transaction.savepoint_commit(sid)
                if id_editing is not None:
                    selector['success'] = 'The exhibition was correctly edited.'
                else:
                    selector['success'] = 'The new exhibition was added.'
            except IntegrityError:
                transaction.savepoint_rollback(sid)
                selector['failure'] = True
        else:
            selector['failure'] = True
        return render(request, self.template_name, selector)