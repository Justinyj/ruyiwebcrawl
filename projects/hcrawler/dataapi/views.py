from django.shortcuts import render
from django.http import HttpResponse

from hcrawler_models import Hentity 

def hprice(request, name):
    Hentity.objects(name=name)
    return HttpResponse("Hello, world. You're at the polls index.")

