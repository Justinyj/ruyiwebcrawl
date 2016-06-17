violence.py：读取 all_urls.txt下的26万个url并获取页面，将每个页面的公司名输出到comany_name.txt。
每行保存一次record，每隔一百行输出一次进度，出现异常页面时停止页面并输出ERROR,(代表可能被反爬，目前还没遇到)。

record.txt：储存读取的位置行数，断点续传。

all_urls.txt：由scrapy爬虫爬取到的页面根据最大页数拼成，每个url的页面包含0-10个公司名.
