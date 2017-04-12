from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class IndexView(TemplateView):
    main_url = '/curator/scheduling'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return redirect(self.main_url)


class CuratorAccount(TemplateView):
    template_name = 'curator/curator-account.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        modifications = {'error': [], 'success': []}
        user = request.user

        fullname = request.POST.get('name', '')
        email = request.POST.get('email', '')

        new_password = request.POST.get('new-password', '')
        confirm_password = request.POST.get('confirm-password', '')

        password = request.POST.get('password', '')

        if len(new_password) > 0:
            if len(confirm_password) > 0\
                    and new_password == confirm_password:
                if len(password) > 0 and user.check_password(password):
                    user.set_password(new_password)
                    modifications['success'].append('Successful password change.')
                else:
                    modifications['error'].append('Incorrect password.')
            else:
                modifications['error'].append('Passwords mismatch.')

        if len(fullname) > 0:
            try:
                first, last = fullname.split(" ", 1)
                user.first_name = first
                user.last_name = last
                modifications['success'].append('Successful name change')
            except ValueError:
                modifications['error'].append('Name must have at least first and last name.')

        if len(email) > 0:
            try:
                validate_email(email)
                user.email = email
                modifications['success'].append('Successful email change')
            except ValidationError:
                modifications['error'].append('Wrong email structure.')

        if len(modifications['error']) != 0:
            modifications['success'] = []
        elif len(modifications['success']) < 1:
            modifications['error'].append('No changes was applied')
        else:
            user.save()
        return render(request, self.template_name, modifications)