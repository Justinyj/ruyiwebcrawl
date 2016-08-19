# API design

## 1.市场价格
* input: /api/v1/hprice//(?P<name>.+)
* output: 

      {
      'nid': '',
      'name': '',
      'mainEntityOfPage': '',
      'description': '',
      'maxPrice': '',
      'minPrice': '',
      'price': '',
      'priceCurrency': '',
      'unitText': '',
      'priceType': '',
      'productionYear': '',
      'validDate': '',
      'seller': '',
      'productGrade': '',
      'productSpecification': '',
      'productPlaceOfOrigin': '',
      'sellerMarket': '',
      'properties': '',
      'createdTime': ''，
      'source': 'http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?random=0.8801452924569142&ycnam=&market=&leibie=&istoday=&paramName=&paramValue=&pageIndex=226&pageSize=20'，
      'site': 'www.yt1998.com/'，
      'confidence': '0.7'，     
      }


## 2.上下游商品
* input: /api/v1/updownstream/(?P<name>.+)
* output: 

    {
    }

## 3.商品描述
* input: /api/v1/desc/(?P<name>.+)
* output: 

    {
    }

## 4.药监局
* input: /api/v1/manufacturer/(?P<drug>.+)
* output: 

    {
    }

## 5.企业（工商注册）
* input: /api/v1/companyinfo/(?P<company>.+)
* output: 

    {
    }