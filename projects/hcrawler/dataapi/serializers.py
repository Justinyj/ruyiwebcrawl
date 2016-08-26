from rest_framework_mongoengine.serializers import DocumentSerializer
from hcrawler_models import Hentity, Hprice, Hmaterial


class HpriceSerializer(DocumentSerializer):
    class Meta:
        model = Hprice
        fields = ('name', 'price', 'validDate', 'sellerMarket', 'source', 'site')

        

        
class HmaterialSerializer(DocumentSerializer):
    class Meta:
        model = Hmaterial
   