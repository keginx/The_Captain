# -*- coding: utf-8 -*-
# @Author : Keginx
import json
import random
import time
import datetime
from urllib.parse import quote
import pandas as pd
import requests


# 通过猫眼电影api接口获取评论和评分等信息
# release_time: 电影上映时间
# movie_id:通过搜索电影获得,例如中国机长url是https://maoyan.com/films/1230121,movie_id就是1230121
def crawling_data(movie_id, release_time):
    ## 设置headers和cookie
    header = {'Host': 'm.maoyan.com',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
              'Accept-Encoding': 'gzip, deflate',
              'DNT': '1',
              'Connection': 'keep-alive',
              'Upgrade-Insecure-Requests': '1',
              'Cache-Control': 'max-age=0'}
    # cookies = 'v=3; iuuid=1A6E888B4A4B29B16FBA1299108DBE9CDCB327A9713C232B36E4DB4FF222CF03; webp=true; ci=1%2C%E5%8C%97%E4%BA%AC; __guid=26581345.3954606544145667000.1530879049181.8303; _lxsdk_cuid=1646f808301c8-0a4e19f5421593-5d4e211f-100200-1646f808302c8; _lxsdk=1A6E888B4A4B29B16FBA1299108DBE9CDCB327A9713C232B36E4DB4FF222CF03; monitor_count=1; _lxsdk_s=16472ee89ec-de2-f91-ed0%7C%7C5; __mta=189118996.1530879050545.1530936763555.1530937843742.18'
    # cookie = {}
    # for line in cookies.split(';'):
    #     name, value = line.strip().split('=', 1)
    #     cookie[name] = value
    # cookie = {'from': {'expires': '1970-01-01T00:00:00.000Z', 'path': '/', 'value': ''}}

    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    realse_time = datetime.datetime.strptime(release_time, '%Y-%m-%d %H:%M:%S')
    # 爬取数据，每次理论上可以爬取1k数据需要多次执行，最后统一去重
    comment_data = pd.DataFrame(columns=['date', 'score', 'city', 'comment', 'nick'])
    # 发表评论的时间
    start_time = now_time

    # 从当前时间往前遍历即从最新评论往前获取数据,当start_time和电影上映时间相同时遍历时结束
    while start_time > release_time:
        print('正在爬取{}之前1000条评论'.format(start_time))

        # 每次只能爬取前1000条数据，每页15条，因此67次循环之后，便不再有数据可以爬取了,需要更新start_time
        for i in range(67):
            print('正在下载第{}页评论'.format(i + 1))
            i *= 15
            try:
                # 一个url例子:
                # http://m.maoyan.com/mmdb/comments/movie/1230121.json?_v_=yes&offset=15&startTime=2019-10-15%2023:59:59
                url = 'http://m.maoyan.com/mmdb/comments/movie/{}.json?_v_=yes&offset={}&startTime={}'.format(
                    str(movie_id), str(i), quote(str(start_time)))
                print(url)
                time.sleep(random.random())
                html = requests.get(url=url, headers=header).content
                # 0条数据则退出循环
                total = json.loads(html.decode('utf-8'))['total']
                if total == 0:
                    break
                data = json.loads(html.decode('utf-8'))['cmts']
                if data:
                    for item in data:
                        comment_data = comment_data.append(
                            {'date': item['time'], 'city': item['cityName'],
                             'score': item['score'], 'comment': item['content'],
                             'nick': item['nick']}, ignore_index=True)
                # 每页中最后一条评论的时间
                last_start_time = data[-1]['startTime']
            except Exception as e:
                print(e)
                continue

        # 获取1000条数据后更新start_time
        start_time = last_start_time
    comment_data.to_csv('resources/data.csv', index=False, line_terminator='\r\n')
    print('爬取数据完毕!')
