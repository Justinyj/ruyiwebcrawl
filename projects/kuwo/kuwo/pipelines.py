# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from kuwo.items import MusicCatItem, PlaylistItem, MusicItem, AlbumItem, ArtistItem, MusicInfoItem,ArtistInfoItem
import codecs

class KuwoPipeline(object):
    def __init__(self):
        # self.fmusicCat = codecs.open("/home/wl/kuwoFile/musicCatFile1.json","w",encoding='utf-8')
        # self.fplaylist = codecs.open("/home/wl/kuwoFile/playlistFile1.json","w",encoding='utf-8')
        self.fmusic = codecs.open("/home/wl/kuwoFile2/musicFile1.json","a",encoding='utf-8')
        self.falbum = codecs.open("/home/wl/kuwoFile2/albumFile.json","a",encoding='utf-8')
        self.fartist = codecs.open("/home/wl/kuwoFile2/artistFile.json","a",encoding='utf-8')
        # self.fmusicInfo = codecs.open("/home/wl/kuwoFile1/musicInfoFile.json","a",encoding='utf-8')
        # self.fartistInfo = codecs.open("/home/wl/kuwoFile1/artistInfoFile.json","a",encoding='utf-8')
    def process_item(self, item, spider):
        if isinstance(item, MusicCatItem):
            self.fmusicCat.write(item['content']+'\n')
        elif isinstance(item, PlaylistItem):
            self.fplaylist.write(item['content']+'\n')
        elif isinstance(item, MusicItem):
            self.fmusic.write(item['content']+'\n')
        elif isinstance(item, AlbumItem):
            self.falbum.write(item['content']+'\n')
        elif isinstance(item, ArtistItem):
            self.fartist.write(item['content']+'\n')
        elif isinstance(item, MusicInfoItem):
            self.fmusicInfo.write(item['content']+'\n')
        elif isinstance(item, ArtistInfoItem):
            self.fartistInfo.write(item['content'] + '\n')
        return item
