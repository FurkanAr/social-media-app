from django.views.generic.base import TemplateView

class HomePageView(TemplateView):

    template_name = "main/home.html"