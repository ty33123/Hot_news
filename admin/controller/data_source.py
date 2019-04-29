import asyncio
import aiohttp
import json
from lxml import etree


async def get_text(url, cookie, encoding):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
    headers['cookie'] = cookie
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            # print(resp.status)
            return await resp.text(encoding=encoding)


async def get_zhihu_hot():
    url = 'https://www.zhihu.com/hot'
    cookie = '知乎cookie'
    result = await get_text(url, cookie, 'utf-8')
    page = etree.HTML(result)
    items = []
    for i in page.cssselect('.HotItem'):
        temp = []
        item = {}
        for j in i.cssselect('.HotItem-index div'):
            temp.append(j.text)
        item['is_new'] = 0
        if len(temp) > 1:
            item['is_new'] = 1
        item['num'] = temp[0]
        for j in i.cssselect('.HotItem-content'):
            item['title'] = j.xpath('./a/h2')[0].text
            item['url'] = j.xpath('./a')[0].get('href')
            hotitem_excerpt = j.cssselect('a p')
            temp = ''
            if len(hotitem_excerpt) > 0:
                temp = hotitem_excerpt[0].text
            item['excerpt'] = temp
            item['hot_count'] = j.xpath('./div/text()')[0]
        items.append(item)
    return items


async def get_baidu_hot():
    url = 'http://top.baidu.com/buzz?b=1&fr=topindex'
    result = await get_text(url, '', 'gbk')
    page = etree.HTML(result)
    items = []
    for i in page.cssselect('.list-table tr'):
        item = {}
        temp = i.cssselect('.first span')
        if len(temp) > 0:
            item['num'] = temp[0].text
        temp = i.cssselect('.keyword .list-title')
        if len(temp) > 0:
            item['title'] = temp[0].text
            item['url'] = temp[0].get('href')
            item['is_new'] = 0
        temp = i.cssselect('.keyword .icon.icon-new')
        if len(temp) > 0:
            item['is_new'] = 1
        temp = i.cssselect('.last span')
        if len(temp) > 0:
            item['hot_count'] = temp[0].text
        if item != {}:
            items.append(item)
    return items


async def get_tieba_hot():
    url = 'http://c.tieba.baidu.com/hottopic/browse/topicList'
    result = await get_text(url, '', 'utf-8')
    data = json.loads(result)['data']['bang_topic']['topic_list']
    items = []
    for d in data:
        items.append(dict(num=d['idx_num'], title=d['topic_name'],
                          hot_count=d['discuss_num'], url=d['topic_url'],
                          is_new=0))
    return items


async def get_weibo_hot():
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    result = await get_text(url, '', 'utf-8')
    page = etree.HTML(result)
    items = []
    for i in page.cssselect('.data table tbody tr'):
        item = {}
        temp = i.cssselect('.td-01')
        if len(temp) > 0:
            if len(temp[0].cssselect('.icon-top')) > 0:
                item['num'] = 'top'
            else:
                item['num'] = temp[0].text
        temp = i.cssselect('.td-02')
        if len(temp) > 0:
            a = temp[0].cssselect('a')
            if len(a) > 0:
                a = a[0]
                item['title'] = a.text
                if a.get('href_to') is not None:
                    item['url'] = 'https://s.weibo.com' + a.get('href_to')
                else:
                    item['url'] = 'https://s.weibo.com'+a.get('href')
            span = temp[0].cssselect('span')
            if len(span) > 0:
                item['hot_count'] = span[0].text
            else:
                item['hot_count'] = '0'
        temp = i.cssselect('.td-03 i')
        if len(temp) > 0:
            if temp[0].text == '新':
                item['is_new'] = 1
            elif temp[0].text == '热':
                item['is_new'] = 2
            elif temp[0].text == '荐':
                item['is_new'] = 3
            elif temp[0].text == '沸':
                item['is_new'] = 4
            else:
                item['is_new'] = 5
        else:
            item['is_new'] = 0
        if item != {}:
            items.append(item)
    return items


def get_hot_news():
    loop = asyncio.new_event_loop()
    # loop = asyncio.get_event_loop()
    # print(loop)
    baidu_hot = loop.run_until_complete(get_baidu_hot())
    zhihu_hot = loop.run_until_complete(get_zhihu_hot())
    weibo_hot = loop.run_until_complete(get_weibo_hot())
    tieba_hot = loop.run_until_complete(get_tieba_hot())
    loop.close()
    return dict(baidu_hot=baidu_hot, zhihu_hot=zhihu_hot, weibo_hot=weibo_hot, tieba_hot=tieba_hot)
