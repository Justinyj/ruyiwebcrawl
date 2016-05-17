#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from dbconnector import dbwrapper

import hashlib
import base64


def db_get_cache(hashkey):
    sql1 = ("select content from contents where cached_id = "
            "(select id from cached where url_hash='{}' "
            "order by created_time desc limit 1);".format(hashkey))
    sql2 = ("select content from contents as a "
            "inner join cached as b on a.cached_id=b.id "
            "where b.url_hash='{}';".format(hashkey))

    try:
        # RowResult(columns=['content'], results=[('WkhWdFpTNWpiMjA9',)])
        ret = dbwrapper.execute(sql1, result=True)
        if ret.results == []:
            return {'success': False}

        html = base64.standard_b64decode(ret.results[0][0])
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True, 'content': html}


def db_set_cache(hashkey, url, batch_id, content):
    sql1 = ("insert into accessed (batch_id, status, url, url_hash) "
            "values ('{}', '{}', '{}', '{}');".format(batch_id, 0, url, hashkey))

    sql2 = ("with inserted as ("
                "insert into cached (url, url_hash, content_hash) values ('{}', '{}', '{}')"
                " RETURNING id )"
            "insert into contents (cached_id, content) values ((select id from inserted), '{}');"
            "".format(url, hashkey, content_hash, base64.standard_b64encode(content)))

    try:
        content_hash = hashlib.sha1(content).hexdigest()
        dbwrapper.execute(sql1)
        dbwrapper.execute(sql2)
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True}


def db_get_all_cache(batch_id):
    """ get all distinct url from all these batches
    """
    sql = ("select max(url) as url, url_hash, max(content) as content, max(created_time) "
           "from (select max(c.content) as content, max(b.url) as url, b.url_hash, b.created_time "
                  "from accessed as a "
                  "left join cached as b on a.url_hash=b.url_hash "
                  "inner join contents as c on b.id=c.cached_id "
                  "where a.batch_id like '{}%' "
                  "group by b.url_hash, b.created_time "
                  "order by b.created_time desc) as result "
           "group by url_hash;".format(re.sub('\d+$', '', batch_id)))
    try:
        ret = dbwrapper.execute(sql).results
        if ret == []:
            return {'success': False}
    except Exception as e:
        return {'success': False, 'error': e}

    result = [(url, url_hash, content) for url, url_hash, content, _ in ret]
    return {'success': True,
            'hash_content_pair': result}

