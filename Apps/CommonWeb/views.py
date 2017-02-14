from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'common-web/index.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class LoginView(TemplateView):
    template_name = 'common-web/login.html'

    def get(self, request, *a, **ka):
        if request.user.is_authenticated():
            return redirect('/curator')
        next_url = request.GET.get('next', None)
        if next_url:
            next_dict = {'next': next_url}
        else:
            next_dict = {}
        return render(request, self.template_name, next_dict)

    def post(self, request):

        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        next_url = request.POST.get('next_url', None)

        if user is None:
            return render(request, self.template_name, {'message': 'Incorrect credentials'})

        else:
            login(request, user)
            if next_url:
                url = next_url
            else:
                url = '/curator'
            return redirect(url)


class LogoutView(TemplateView):

    def get(self, request, *a, **ka):
        logout(request)
        return redirect('/')
