import copy

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.decorators import group_required
from Apps.Curator.models.museums import Room, Museum
from Apps.Curator.models.opinions import Opinion


@transaction.atomic
def confirm_opinion(key):
    opinions = Opinion.objects.filter(hash_key=key).filter(validated=False)

    if len(opinions) < 1:
        return False

    opinion = opinions[0]
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
def query_opinion(museum_id, approved, pending):
    opinion_list = list()

    if not approved and not pending:
        return opinion_list

    selected_museum = Museum.objects.get(id=museum_id)
    opinions = Opinion.objects.filter(validated=True).filter(museum=selected_museum)
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
    selector = {'header': {'display': 'Select a Museum from the list:',
                           'selected': 'selected'},
                'options': [],
                'approved': '',
                'pending': ''}

    def get_current_selector(self):
        current_selector = copy.deepcopy(self.selector)
        museums = get_museums_data()
        for museum in museums:
            museum_template = {'id': museum['id'], 'display': museum['name'], 'selected': ''}
            current_selector['options'].append(museum_template)
        return current_selector

    @method_decorator(group_required('Opinion_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        current_selector = self.get_current_selector()
        return render(request, self.template_name, current_selector)

    @method_decorator(group_required('Opinion_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        current_selector = self.get_current_selector()

        current_museum = request.POST.get('museum', None)
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

        if current_museum is not None:
            current_selector['current_museum'] = current_museum
            current_selector['header']['selected'] = ''
            for option in current_selector['options']:
                if option['id'] == int(current_museum):
                    option['selected'] = 'selected'
                    break

            opinions = query_opinion(current_museum, approved, pending)
            current_selector['opinions'] = opinions

        return render(request, self.template_name, current_selector)


@transaction.atomic
def delete_timeout_opinions():
    today = datetime.today().date()
    opinions = Opinion.objects.filter(validated=False).filter(timeout__lt=today)

    sid = transaction.savepoint()

    try:
        for opinion in opinions:
            opinion.delete()
    except IntegrityError:
        transaction.savepoint_rollback(sid)
        return False

    transaction.savepoint_commit(sid)
    return True


class OpinionDeleterView(TemplateView):

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        response = {'status': 409}
        if delete_timeout_opinions():
            response['status'] = 200

        return JsonResponse(response)
