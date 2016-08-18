#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from mongoengine import *
from datetime import datetime

connect(db=DB, alias=DB, host=MONGODB_HOST)

class Hentity(Document):
    nid = StringField()
    ns = StringField() # namespace
    s_label = StringField() # name
    s_rank = StringField() # 搜索结果数
    sameas = ListField(StringField()) # 实体链接
    alias = ListField(StringField()) # 别名

    meta = {
        'indexes': ['nid', 's_label'],
    }

class Hmaterial(Document):
    name = StringField() # 名字
    description = StringField() # 描述
    category = StringField() # 分类
    drug_form = StringField() # 剂型
    properties = DictField() # 属性
    upstream_material = ListField(StringField()) # 上游产品
    downstream_material = ListField(StringField()) # 下游产品
    createdTime = DateTimeField(default=datetime.now)
    source = StringField()
    confidence = StringField()

    meta = {
        'indexes': ['name'],
    }

class Hprice(Document):
    name = StringField()
    mainEntityOfPage = StringField() # 实体
    description = StringField()
    maxPrice = StringField() # 价格最大值
    minPrice = StringField() # 价格最小值
    price = StringField()
    priceCurrency = StringField() # 报价币种
    unitText = StringField() # 价格单位，比如：元/吨
    priceType = StringField() # 价格类型，比如：车皮价
    productionYear = StringField() # 生产日期
    validDate = StringField() # 报价日期
    seller = StringField() # 销售商
    productGrade = StringField() # 商品等级
    productSpecification = StringField() # 商品说明
    productPlaceOfOrigin = StringField() # 商品产地
    sellerMarket = StringField() # 卖场
    properties = DictField() # 属性
    createdTime = DateTimeField(default=datetime.now)
    source = StringField()
    confidence = StringField()


    meta = {
        'indexes': ['mainEntityOfPage', ('name', 'validDate', 'productGrade', 'sellerMarket')],
    }

class Supplier(Document):
    company_name = StringField()
    unified_social_credit_code = StringField()
    registration_id = StringField()
    organization_code = StringField()
    status = StringField()
    business_type = StringField()
    establish_date = StringField()
    legal_person = StringField()
    registered_capital = StringField()
    begin = StringField()
    end = StringField()
    registration_authority = StringField()
    approval_date = StringField()
    address = StringField()
    business_scope = StringField()
    createdTime = DateTimeField(default=datetime.now)
    source = StringField()
    confidence = StringField()

    company_info = EmbeddedDocumentField()
    gmp_info = ListField(EmbeddedDocumentField(GmpInfo))
    medicines_info = ListField(EmbeddedDocumentField(MedicinesInfo))

    shareholders = ListField(EmbeddedDocumentField(Shareholders))
    executives = ListField(EmbeddedDocumentField(Executives))
    branches = ListField(EmbeddedDocumentField(Branches))
    changes = ListField(EmbeddedDocumentField(Changes))
    abnormals = ListField(EmbeddedDocumentField(Abnormals))

    meta = {
        'indexes': ['legal_person', 'company_name']
    }


class CompanyInfo(EmbeddedDocument):
    fax = StringField()
    telephone = StringField()
    cellphone = StringField()
    contacts = StringField()
    website = StringField()
    email = StringField()
    paymentMethod = StringField() # 付款方式
    shippingFee = StringField() # 运输费用
    supplierGrade = StringField() # 供应商评级
    cooperationIntention = StringField() # 合作意向
    productList = ListField(StringField())


class GmpInfo(EmbeddedDocument):
    province = StringField()
    certification_number = StringField()
    certification_version = StringField()
    scope_of_certification = StringField()
    begin_date = DateTimeField()
    end_date = DateTimeField()

class MedicinesInfo(EmbeddedDocument):
    license_number = StringField()
    standard_code = StringField()
    license_data = StringField()
    specification = StringField()
    standard_code_remark = StringField()


class Shareholders(EmbeddedDocument):
    name = StringField()
    role = StringField()
    subscribe_money = StringField()
    subscribe_time = StringField()
    actual_money = StringField()
    actual_time = StringField()

class Executives(EmbeddedDocument):
    name = StringField()
    position = StringField()

class Branches(EmbeddedDocument):
    name = StringField()
    link = StringField()

class Changes(EmbeddedDocument): 
    project = StringField()
    change_time = StringField()
    before_change = StringField()
    after_change = StringField()

class Abnormals(EmbeddedDocument):
    date = StringField()
    organs = StringField()
    reason = StringField()
    end_date = StringField()
    end_reason = StringField()


class Purchase(Document):
    name = StringField()
    mainEntityOfPage = StringField()
    orderDate = StringField()
    validFrom = StringField()
    validThrough = StringField()
    price = StringField()
    priceCurrency = StringField() # 报价币种
    priceType = StringField() # 价格类型，比如：车皮价
    unitText = StringField() # 价格单位，比如：元/吨
    orderNumber = StringField() # 总量
    totalPrice = StringField() # 总价
    paymentMethod = StringField() # 付款方式
    shipping = StringField() # 运输方式
    shippingFee = StringField() # 运输费用
    storageMode = StringField() # 仓促方式
    productGrade = StringField() # 商品等级

    createdTime = DateTimeField(default=datetime.now)
    source = StringField()
    confidence = StringField()

    meta = {
        'indexes': ['mainEntityOfPage', 'name'],
    }


class News(Document):
    title = StringField()  # 标题
    content = StringField() # 内容
    pubdate = DateTimeField()
    source = StringField()
    createdTime = DateTimeField(default=datetime.now)
    confidence = StringField()

    meta = {
        'indexes': ['title', 'pubdate'],
    }


class Confidence(Document):
    website = StringField()
    confidence = StringField()


class ProductionCapacity(Document):
    supplier = ReferenceField(Supplier)
    productPlaceOfOrigin = StringField() # 商品产地
    turnout = StringField() # 产量
    plant_area = StringField() # 种植面积
    validDate = StringField() # 产能年份
    validFrom = StringField()
    validThrough = StringField()

