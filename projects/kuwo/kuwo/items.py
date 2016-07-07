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

class MusicCatItem(scrapy.Item):
    content = scrapy.Field()

class PlaylistItem(scrapy.Item):
    content = scrapy.Field()

class ArtistItem(scrapy.Item):
    content = scrapy.Field()

class AlbumItem(scrapy.Item):
    content = scrapy.Field()

class MusicItem(scrapy.Item):
    content = scrapy.Field()

class MusicInfoItem(scrapy.Item):
    content = scrapy.Field()

class ArtistInfoItem(scrapy.Item):
    content = scrapy.Field()