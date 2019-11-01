# 用Python获取猫眼30万短评,解读《中国机长》全国热度
使用Python获取猫眼30万短评,解读《中国机长》分析全国粉丝分布情况解读全国热度, 并利用Pyechart、Pandas、jieba分词生成热力图、玫瑰图、词云等.
 

## 1. **环境要求**

Python3.X+PyEcharts+地图文件包

```python
# 安装pyecharts
pip install pyecharts==0.5.5

# 安装地图文件包
pip install echarts-china-provinces-pypkg # 中国省、市、县、区地图
pip install echarts-china-cities-pypkg
pip install echarts-china-counties-pypkg
pip install echarts-china-misc-pypkg 
pip install echarts-countries-pypkg # 全球国家地图
pip install echarts-united-kingdom-pypkg
```

## 2. **数据获取**

 调用猫眼评论数据接口

> **http://m.maoyan.com/mmdb/comments/movie/1230121.json?_v_=yes&offset=15&startTime=2019-10-15%2023:59:59**

其中**1230121**是电影id, **offset**是偏移值取值范围是0-1000, 每次爬取结果只有15条评论, 所以 offset每次增加15. **startTime=2019-10-15 2023:59:59**表示获取该时间段之前的数据. 当offset递增到1000时就需要把**startTime**更新成第1000条评论中的时间, 如此循环直到**startTime**更新成电影上映时间就结束获取数据.
![获取电影id](https://img-blog.csdnimg.cn/20191030080935861.jpg)

#####  爬取猫眼短评代码实现
评论数据是在最后才写入到csv文件的, 优化的话可以改成多次分批追加数据到文件从而避免数据丢失.  另外还可以用多线程实现来提升爬取速度但是很有可能被加到黑名单.
```python
import json
import random
import time
import datetime
from urllib.parse import quote
import pandas as pd
import requests

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

    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    realse_time = datetime.datetime.strptime(release_time, '%Y-%m-%d %H:%M:%S')
    # 爬取数据，每次理论上可以爬取1k数据，存在大量重复数据，需要多次执行，最后统一去重
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
                #http://m.maoyan.com/mmdb/comments/movie/1230121.json?_v_=yes&offset=15&startTime=2019-10-15%2023:59:59
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
              
```
<br>

#####    数据文件结构
<br>![csv文件结构](https://img-blog.csdnimg.cn/20191101075236205.png)
<br>

 ## 3. 数据解读

##### 全国评论分布状况
![中国机长全国热力图](https://img-blog.csdnimg.cn/20191030233414369.png)从热度图上可以看出大部分评论者位于我国东部, 这基本与我国人口分布和全国经济水平区域分布一致.只差右下角没被点亮了.
<br>
#####  全国主要城市评论数和打分情况TOP20
![主要城市评论数](https://img-blog.csdnimg.cn/20191031081829324.png)<br>
北上广深位于前五继续宣示着中国一线城市的地位, 值得注意的是成都评论人数领先于上海说明成都人民挺支持英雄机长的毕竟川航挡风玻破碎后飞机就在成都备降, 东莞位于第六远远超过后面一大票省会城市( 嘿嘿,东莞要崛起了毕竟华为都开始搬到东莞了  <img src="https://img-blog.csdnimg.cn/20191031201710617.jpg" width = 20 height =20 align="center" /> )  
至于各大城市评分嘛,最高平均分4.84分、最低分4.7分,啧啧这分数，不管你信不信我反正是不信. 波动范围.在4.6到4.8之间各大城市表现简直一模一样. 
<br><br>
#####  评分星级玫瑰图
<br>

![评分星级](https://img-blog.csdnimg.cn/2019103122414296.png)<br>
 绝大评论者都给了五星好评, 少部分给了一星差评. 不知道五星好评能返现不 :joy:
<br><br>
#####  生成词云
![词云](https://img-blog.csdnimg.cn/20191031225009346.jpg)<br>
词云主要词语是震撼、真实、敬畏、感动、好看，表明该片在国庆档上映取得了不错的口碑用来给祖国母亲庆生也是极好的. 在空难片中应该算中等水平. 之前刷B站看到了九筒解说二十年前拍的国产首部空难片[《紧急迫降》](https://www.bilibili.com/video/av71198947)突然让我回忆起童年看过的电影频道 , 该片是根据东航客机起落架放不下通过各种操作最后惊险迫降上海虹桥机场的故事改编，即使在现在看来也是相当不错的影片. 希望国产影片能越做越好吧. :grinning:

<br>

 ## 4. 代码实现
  <br>
   
#####  数据处理
用pandas 加载数据文件data.csv去重后写入到drop_duplicates_data.csv, 按照城市进行聚合获取每个城市的评论人数和平均评分. 还可以按照用户名nick去重, 另外行结束符line_terminator可以是自定义的一串特定字符这样按行读取的时候就可以避免内容包含回车换行引起的错误. 需要注意的是score列 需要转成float类型
```python
import pandas as pd
import traceback
from pyecharts import Bar, Geo, Line, Overlap, Pie

## 可以直接读取我们已经爬到的数据进行分析,score列转成float类型
try:
    comment_data = pd.read_csv('resources/data.csv', encoding="GBK", dtype={'score': float})
except Exception as e:
    pass
    print(traceback.format_exc())

# 去重
comment_data = comment_data.drop_duplicates()
comment_data.to_csv('resources/drop_duplicates_data.csv', index=False, line_terminator='\r\n')

grouped = comment_data.groupby(['city'])

grouped_pct = grouped['score']
# 按城市分组后进行聚合
city_com = grouped_pct.agg(['mean', 'count'])

# 重置连续行索引,
# 可以看到此时获得了新的index列，而原来的index变成了我们的数据列，保留了下来。drop=True删除原index
city_com.reset_index(inplace=True)
# round四舍五入两位精度
city_com['mean'] = round(city_com['mean'], 2)
```
<br>

#####  热力图
热度图地图坐标不匹配可以修改坐标文件**site-packages/pyecharts/datasets/city_coordinates.json**, 参考 [https://www.cnblogs.com/mylovelulu/p/9511369.html](https://www.cnblogs.com/mylovelulu/p/9511369.html)
```python
## 全国热力图
def generate_heatmap(title):
    data = [(city_com['city'][i], city_com['count'][i]) for i in range(0, city_com.shape[0])]
    geo = Geo(title, title_color="#fff",
              title_pos="center", width=1200, height=600, background_color='#404a59')
    attr, value = geo.cast(data)
    attr_list = []
    value_list = []
    len = attr.__len__()
    for i in range(len):
        try:
            attr_list.append(attr[i])
            value_list.append(value[i])
            geo.add("city", attr_list, value_list, visual_range=[0, 200], maptype='heatmap', visual_text_color="#000",
                    symbol_size=10, is_visualmap=True)

        except ValueError as e:
            print(e)
            attr_list.remove(attr[i])
            value_list.remove(value[i])
            continue

    geo = Geo(title, title_color="#fff",
              title_pos="center", width=1200, height=600, background_color='#404b59')
    geo.add("city", attr_list, value_list, visual_range=[0, 3500], maptype='china', border_color='fff',
            visual_text_color="#fff",
            symbol_size=5, is_visualmap=True)
    # geo.show_config()
    geo.render('resources/heat_map.html')
```
<br>


#####  直方图及折线图
获取排名前20的城市评论数据
```python
## 主要城市评论数与评分
def generate_score_tabale():
    city_main = city_com.sort_values('count', ascending=False)[0:20]
    attr = city_main['city']
    v1 = city_main['count']
    v2 = city_main['mean']
    line = Line("主要城市平均评分")
    line.add("主要城市平均评分", attr, v2, is_stack=True, xaxis_rotate=50, yaxis_min=4.0,
             mark_point=['min', 'max'], xaxis_interval=0, line_color='lightblue',
             line_width=4, mark_point_textcolor='yellow', mark_point_color='lightblue',
             is_splitline_show=False)

    bar = Bar("主要城市评论数及评分")
    bar.add("主要城市评论数", attr, v1, is_stack=True, xaxis_rotate=50, yaxis_min=0,
            xaxis_interval=0, is_splitline_show=False)
    overlap = Overlap()
    # 默认不新增 x y 轴，并且 x y 轴的索引都为 0
    overlap.add(bar)
    overlap.add(line, yaxis_index=1, is_add_yaxis=True)
    overlap.render('resources/city_score.html')

```
<br>


#####  玫瑰图
评分0.5-1为一星, 其余以此类推
```python
# 生成评分星级比例
def generate_star_pie(title):
    # 定义星级，并统计各星级评分数量
    attr = ['五星', '四星', '三星', '二星', '一星']
    scores = list(comment_data['score'])
    value = [
        scores.count(5) + scores.count(4.5),
        scores.count(4) + scores.count(3.5),
        scores.count(3) + scores.count(2.5),
        scores.count(2) + scores.count(1.5),
        scores.count(1) + scores.count(0.5)
    ]
    pie = Pie(title, title_pos='right', width=1000)
    pie.add('评分星级', attr, value, center=[75, 50], is_random=True,
            radius=[40, 75], rosetype='area',
            is_legend_show=True, is_label_show=True)
    pie.render('resources/score_star_pie.html')

```
<br>


#####  词云
生成词云时最开始只能生成几个词, 最后发现是因为Counter对象里面包含了回车换行符号 **"\r\n"** , 这是Pillow的一个bug  [https://github.com/python-pillow/Pillow/issues/2614](https://github.com/python-pillow/Pillow/issues/2614)   删除 **"\r\n"** 后成功生成词云. 选择词云图片的时候尽量选白色底背景、轮廓清晰并且色彩丰富的, 不然生成的词云图片就没有灵魂 ,  哈哈哈:sunglasses:
```python
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

```
<br>

#####  完整代码

> [https://github.com/keginx/The_Captain](https://github.com/keginx/The_Captain)

<br>

##### 文件结构

```bash
The_Captain/
├── analysis.py                       读取并处理数据,生成热力图、直方图、玫瑰图
├── data_sets.py                      获取猫眼短评接口数据
├── main.py                           主函数入口
├── README.md
├── resources                         资源文件夹
│   ├── city_score.html               全国主要城市评论数和打分情况TOP20
│   ├── data.csv                      用于存放获取到的评论数据
│   ├── drop_duplicates_data.csv      用于存放去重后的评论数据
│   ├── heat_map.html                 生成的热力图
│   ├── image.jpg                     词云的参考图片
│   ├── score_star_pie.html           生成的评分星级比例图
│   ├── STKAITI.TTF                   字体文件，用于避免汉字不能显示的问题
│   └── word_cloud.jpg                生成的词云图片
└── word_cloud.py                     用于生成词云
```
<br>


#####  参考

 - [3天破9亿！上万条评论解读《西虹市首富》是否值得一看](https://juejin.im/post/5b5fd11c6fb9a04fe548ff7b#comment)
 - [一步步带你找猫眼评论的接口4月14号](https://www.cnblogs.com/fodalaoyao/p/10707080.html)
 - [《一出好戏》讲述人性，使用Python抓取猫眼近10万条评论并分析，一起揭秘“这出好戏”到底如何？](https://www.cnblogs.com/mylovelulu/p/9511369.html)
 - [font.getsize fail with empty strings](https://github.com/python-pillow/Pillow/issues/2614)
