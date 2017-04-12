import copy
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.models.museums import Room, Museum
from Apps.Curator.models.opinions import Opinion


@transaction.atomic
def confirm_opinion(key):
    opinion = Opinion.objects.get(hash_key=key)
    if opinion.validated:
        return False
    opinion.validated = True
    opinion.save()
    return True


class OpinionHashView(TemplateView):
    template_name = 'common-web/opinion_confirmation.html'

    def get(self, request, *a, **ka):
        hash_value = request.GET.get('key', None)
        results = {'title': 'Confirmation Error',
                   'body': 'The opinion you are trying to confirm is invalid or the code has expired.'}

        if hash_value is not None:
            if confirm_opinion(hash_value):
                results = {'title': 'Confirmation Successful!',
                           'body': 'Thanks for submitting your opinion!'}

        return render(request, self.template_name, results)


@transaction.atomic
def get_museums_data():
    museums_list = list()
    museums = Museum.objects.all()
    for museum in museums:
        museums_list.append({'name': museum.name, 'id': museum.id})
    return museums_list


@transaction.atomic
def delete_opinion(opinion_id):
    opinion = Opinion.objects.get(id=opinion_id)
    opinion.delete()


@transaction.atomic
def reverse_opinion_status(opinion_id):
    opinion = Opinion.objects.get(id=opinion_id)
    opinion.status = not opinion.status
    opinion.save()


@transaction.atomic
def query_opinion(room_name, approved, pending):
    opinion_list = list()

    if not approved and not pending:
        return opinion_list

    selected_room = Room.objects.get(name=room_name)
    opinions = Opinion.objects.filter(validated=True).filter(room=selected_room)
    if approved and not pending:
        opinions = opinions.exclude(status=False)
    elif pending and not approved:
        opinions = opinions.exclude(status=True)

    for opinion in opinions:
        opinion_template = dict()
        opinion_template['id'] = opinion.id
        opinion_template['name'] = opinion.person_name
        opinion_template['opinion'] = opinion.opinion
        opinion_template['avatar'] = opinion.avatar
        opinion_template['status'] = opinion.status
        opinion_template['email'] = opinion.email

        opinion_list.append(opinion_template)
    return opinion_list


class OpinionsView(TemplateView):
    template_name = 'curator/opinions.html'
    selector = {'header': {'display': 'Select a Room from the list:',
                           'selected': 'selected'},
                'options': [],
                'approved': '',
                'pending': ''}

    def get_current_selector(self):
        current_selector = copy.deepcopy(self.selector)
        rooms = get_museums_data()
        for room in rooms:
            room_template = {'value': room['name'], 'display': room['name'], 'selected': ''}
            current_selector['options'].append(room_template)
        return current_selector

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        current_selector = self.get_current_selector()
        return render(request, self.template_name, current_selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        current_selector = self.get_current_selector()

        current_room = request.POST.get('room', None)
        checkbox_approved = request.POST.get('approved', None)
        checkbox_pending = request.POST.get('pending', None)
        opinion_id = request.POST.get('id_opinion', None)

        reverse_option = request.POST.get('reverse', None)
        delete_option = request.POST.get('delete', None)

        if reverse_option is not None and reverse_option in ['1']:
            reverse_opinion_status(opinion_id)

        elif delete_option is not None and delete_option in ['1']:
            delete_opinion(opinion_id)

        approved = False
        pending = False

        if checkbox_approved is not None:
            current_selector['approved'] = 'checked'
            approved = True
        if checkbox_pending is not None:
            current_selector['pending'] = 'checked'
            pending = True

        if current_room is not None:
            current_selector['current_room'] = current_room
            current_selector['header']['selected'] = ''
            for option in current_selector['options']:
                if option['value'] == current_room:
                    option['selected'] = 'selected'
                    break

            opinions = query_opinion(current_room, approved, pending)
            current_selector['opinions'] = opinions

        return render(request, self.template_name, current_selector)