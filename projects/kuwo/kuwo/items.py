# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class KuwoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MusicCatItem(scrapy.Item):   #music from user's playlist
    content = scrapy.Field()

class PlaylistItem(scrapy.Item):   #user's playlist
    content = scrapy.Field()

class ArtistItem(scrapy.Item):     #artist 
    content = scrapy.Field()

class AlbumItem(scrapy.Item):      #artist's album
    content = scrapy.Field()

class MusicItem(scrapy.Item):      #music from artist
    content = scrapy.Field()

class MusicInfoItem(scrapy.Item):     #music information, lick lrc
    content = scrapy.Field()

class ArtistInfoItem(scrapy.Item):    #artist information, some text 
    content = scrapy.Field()
