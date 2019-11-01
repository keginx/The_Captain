# -*- coding: utf-8 -*-
# @Author : Keginx
from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator
import jieba
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd


def generate_wordcloud(stopwords):
    ## 绘制词云
    comment_data = pd.read_csv('resources/drop_duplicates_data.csv', encoding="GBK", dtype={'score': float})
    grouped = comment_data.groupby(['city'])
    grouped_pct = grouped['score']

    comments_str = ' '.join(comment_data['comment'])
    words_list = []
    word_generator = jieba.cut_for_search(comments_str)
    for word in word_generator:
        words_list.append(word)
    words_list = [k for k in words_list if len(k) > 1]
    back_color = mpimg.imread('resources/image.jpg')  # 解析该图片
    wc = WordCloud(background_color='white',  # 背景颜色
                   max_words=1000,  # 最大词数
                   mask=back_color,  # 以该参数值作图绘制词云，这个参数不为空时，width和height会被忽略
                   max_font_size=70,  # 显示字体的最大值
                   font_path="resources/STKAITI.TTF",  # 解决显示乱码问题，可进入C:/Windows/Fonts/目录更换字体
                   random_state=42,  # 为每个词返回一个PIL颜色
                   stopwords=stopwords,
                   # width=1000,  # 图片的宽
                   # height=860  #图片的长
                   )
    word_count = Counter(words_list)
    # 删除字典里面的回车换行,避免Pillow的bug
    # size, offset = self.font.getsize(text, direction, features)
    # https://github.com/python-pillow/Pillow/issues/2614
    del (word_count['\r\n'])

    print(word_count)

    # plt.imshow(back_color)

    wc.generate_from_frequencies(word_count)
    # # 基于彩色图像生成相应彩色
    image_colors = ImageColorGenerator(back_color)
    # plt.imshow(wc)
    # 绘制结果
    plt.axis('off')
    plt.figure()
    plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis('off')
    plt.show()
    wc.to_file('resources/word_cloud.jpg')
