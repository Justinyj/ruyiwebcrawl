from django.shortcuts import render
from django.http import HttpResponse

from hcrawler_models import Hentity, Hprice

def hprice(request, name):
    ret = Hentity.objects(alias__in=[name])
    if not ret:
        ret = Hprice.objects(name=name)
    else:
        ret = Hprice.objects(nid=ret.nid)
    return HttpResponse(ret)

