#  импортируем CreateView, чтобы создать ему наследника
#  функция reverse_lazy позволяет получить URL
#  по параметру "name" функции path()
#  берём, тоже пригодится
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("signup")
    template_name = "signup.html"
