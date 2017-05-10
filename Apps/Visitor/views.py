import hashlib
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.html import escapejs
from django.views.generic import TemplateView

from Apps.Curator.models.museums import UnityExhibit, Exhibit
from Apps.Curator.models.opinions import Opinion
from Apps.Curator.models.scheduling import Exhibition
from Apps.Curator.views.resources import parse_inner_url
from VirtualMuseumsFramework.settings import WEBSITE_BASE_URL, WEBSITE_AUTOMATIC_RESPONSE_EMAIL, WEBSITE_SMTP_SERVER


@transaction.atomic
def get_current_expositions():
    today = datetime.today().date()
    expositions = Exhibition.objects.filter(status=True).filter(start_date__lte=today).filter(end_date__gte=today)

    arguments = {'expositions': []}

    for exposition in expositions:
        expo = dict()
        expo['id'] = exposition.id
        expo['name'] = exposition.name
        expo['start_time'] = exposition.start_date.strftime("%B %d, %Y")
        expo['end_time'] = exposition.end_date.strftime("%B %d, %Y")
        arguments['expositions'].append(expo)

    return arguments


@transaction.atomic
def increase_visitor(exposition_id):
    exposition = Exhibition.objects.get(id=exposition_id)
    exhibit = exposition.exhibits.all()[0]
    exhibit.visitors += 1
    exhibit.save()


@transaction.atomic
def get_unity_exhibit(exhibit):

    arguments = dict()

    arguments['title'] = exhibit.name
    arguments['id'] = exhibit.id

    exhibit = UnityExhibit.objects.get(id=exhibit.id)
    arguments['data'] = parse_inner_url(exhibit.data.url)
    arguments['js'] = parse_inner_url(exhibit.javascript.url)
    arguments['mem'] = parse_inner_url(exhibit.memory.url)
    arguments['total_memory'] = exhibit.memory_to_allocate

    return arguments


class IndexView(TemplateView):
    template_name = 'visitor/index.html'

    def get(self, request, *a, **ka):
        arguments = get_current_expositions()
        if len(arguments['expositions']) < 1:
            return redirect('/visitor/error')
        return render(request, self.template_name, arguments)


MUSEUM_TYPES = {
    'Unity': {'get': get_unity_exhibit,
              'template': 'visitor/visualizations/unity-visualization.html'}
}


class VisualizationView(TemplateView):

    def get(self, request, *a, **ka):
        return redirect('/visitor/error')

    def post(self, request, *a, **ka):
        exposition_id = request.POST.get('exposition', '')

        if len(exposition_id) < 1:
            return redirect('/visitor/error')

        exposition = Exhibition.objects.filter(id=exposition_id).filter(status=True)

        if len(exposition) < 1:
            return redirect('/visitor/error')

        exhibit = exposition[0].exhibits.all()[0]
        exhibit_type = exhibit.exhibit_type.name

        arguments = MUSEUM_TYPES[exhibit_type]['get'](exhibit)
        template = MUSEUM_TYPES[exhibit_type]['template']

        if arguments is None:
            return redirect('/visitor/error')

        increase_visitor(exposition_id)

        return render(request, template, arguments)


@transaction.atomic
def get_next_exposition():
    today = datetime.today().date()
    exposition = Exhibition.objects.filter(status=True).filter(start_date__gte=today).order_by('start_date')

    if len(exposition) < 1:
        return None

    exposition = exposition[0]
    next_date = exposition.start_date

    return next_date


class NoExpositionView(TemplateView):
    template_name = 'visitor/no_expositions.html'

    def get(self, request, *a, **ka):
        arguments = dict()
        arguments['title'] = 'An error with the expositions just happened!'

        next_date = get_next_exposition()
        if next_date is None:
            arguments['body'] = 'There is no exposition active at this moment'
        else:
            arguments['body'] = 'The next active exposition is on ' + next_date.strftime("%B %d, %Y")
        return render(request, self.template_name, arguments)


def generate_hash_key(email):
    date = datetime.today()

    random_list = [email, date.strftime('%d%m%Y%H%M%S%f%z')]
    random.shuffle(random_list)
    string = "".join(random_list)
    hash_key = hashlib.sha512(string).hexdigest()
    return hash_key


def send_email(name, exhibit_name, opinion, hash_key, email):
    # TODO develop process
    return True
    from_email = WEBSITE_AUTOMATIC_RESPONSE_EMAIL
    to_email = email

    message = "Good day " + name + ",\n\n" + \
              "This is an information email to validate the opinion you had sent to our museum.\n\n" + \
              "The specific exposition: " + exhibit_name + "\n" + \
              "Your opinion: " + opinion + "\n\n" + \
              "To validate this, please click the next url or copy-paste it into your browser. \n\n" + \
              "<a href=http://" + WEBSITE_BASE_URL + "/confirmation?key?=" + hash_key + ">" + \
              "http://" + WEBSITE_BASE_URL + "/confirmation?key?=" + hash_key + "</a>" + \
              "\n\n" + "Please don't answer this email. It was automatically generate."

    recipients = [to_email, from_email]

    msg = MIMEText(message.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = "Virtual Museum: Opinion validation."
    msg['From'] = from_email
    msg['To'] = ", ".join(recipients)

    try:
        server = smtplib.SMTP(WEBSITE_SMTP_SERVER)
        server.connect()
    except (smtplib.SMTPException, IOError):
        return False
    text = msg.as_string()

    try:
        server.sendmail(from_email, recipients, text)
    except smtplib.SMTPException:
        return False

    return True


class OpinionsView(TemplateView):
    template_name = 'visitor/opinions.html'

    def get(self, request, *a, **ka):
        arguments = dict()
        exhibit_id = request.GET.get('id', None)
        if exhibit_id is not None:
            arguments['exhibit_id'] = exhibit_id
        return render(request, self.template_name, arguments)

    def post(self, request, *a, **ka):
        arguments = {'error': [], 'success': []}

        exhibit_id = request.POST.get('exhibit', '')
        exhibit = None

        try:
            if len(exhibit_id) < 1:
                raise ObjectDoesNotExist()
            exhibit = Exhibit.objects.get(id=exhibit_id)
        except ObjectDoesNotExist:
            arguments['error'].append('Invalid form. Please send your opinion from the exposition interface.')

        arguments['exhibit_id'] = exhibit_id

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        opinion = request.POST.get('opinion', '')
        rating = request.POST.get('rating', '')

        if rating not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            arguments['error'].append('Invalid rating value.')

        if len(name) < 1:
            arguments['error'].append('Please input a non-empty name.')

        try:
            if len(email) < 1:
                raise ValidationError('Empty email.')
            validate_email(email)
        except ValidationError:
            arguments['error'].append('Please input a non-empty email.')

        if len(opinion) < 1:
            arguments['error'].append('Please input a non-empty opinion.')

        opinion = escapejs(opinion)

        if len(arguments['error']) < 1:
            new_opinion = Opinion()
            new_opinion.person_name = name
            new_opinion.email = email
            new_opinion.opinion = opinion
            new_opinion.rating = int(rating)
            hash_key = generate_hash_key(email)
            new_opinion.hash_key = hash_key
            new_opinion.exhibit = exhibit

            one_day_after = datetime.today() + timedelta(days=1)
            one_day_after = one_day_after.date()

            new_opinion.timeout = one_day_after

            if send_email(name, exhibit.name, opinion, hash_key, email):
                new_opinion.save()
                arguments['success'].append('A confirmation email was sent to your address to validated your opinion.')
            else:
                arguments['error'].append('A problem occurred sending the verification email. Please try again later.')

        return render(request, self.template_name, arguments)
