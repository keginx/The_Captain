# -*- coding: utf-8 -*-
# @Author : Keginx
# Date : 2019/10/4

from data_sets import *
from wordcloud import STOPWORDS

if __name__ == '__main__':

    movie_id = '1230121'
    # 电影上映时间,时间格式需要保持一致
    release_date = '2019-09-30 08:00:00'
    crawling_data(movie_id, release_date)

    from analysis import *

    # 热度图标题
    title = '《中国机长》全国热力图'
    generate_heatmap(title)
    generate_score_tabale()

    title = '《中国机长》评分星级比例'
    generate_star_pie(title)

    from word_cloud import generate_wordcloud

    # 设置停用词
    stopwords = set(STOPWORDS)
    word_list = [u'中国', u'机长', u'哈哈', u'非常', u'飞机',u'电影','超级']
    for word in word_list:
        stopwords.add(word)
    generate_wordcloud(stopwords=stopwords)
