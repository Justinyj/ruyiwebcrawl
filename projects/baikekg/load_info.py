#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from hzlib.libfile import read_file, write_file

def zgdbk_extract_info():
    pairs = []

    content = read_file('zgdbk.txt')
    infos = re.findall('<span id="span2" class="STYLE2">(.+?)</span.+?<span id="span14".+?</SRIPT>(.+?)</table>', content, re.S)
    for i in infos:
        entity = zgdbk_parse_entity(i[0])
        if entity is None:
            continue

        info = i[1][:i[1].rfind('</span>')]
        info = lxml.html.fromstring(info.decode('utf-8')).text_content()
        pairs.append( json.dumps({entity: info}) )

    write_file('zgdbk_result.txt', pairs)

