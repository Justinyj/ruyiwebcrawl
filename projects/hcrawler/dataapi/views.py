from django.shortcuts import render
from django.http import JsonResponse
from serializers import HpriceSerializer, HmaterialSerializer
from rest_framework.response import Response
from hcrawler_models import Hentity, Hprice, Hmaterial
from rest_framework.decorators import api_view

@api_view(['GET'])
def hprice(request, name):
    # print name
    ret = Hentity.objects(alias__in=[name])
    if not ret:
        ret = Hprice.objects(name=name)
    else:
        ret = Hprice.objects(nid=ret[0].nid)
    serializer = HpriceSerializer(ret, many=True)
    return Response(serializer.data)
    
@api_view(['GET']) 
def updownstream(request, name):
    ret = Hmaterial.objects(name=name)
    serializer = HmaterialSerializer(ret, many=True)
    return Response(serializer.data)

