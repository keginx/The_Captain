# -*- coding: utf-8 -*-
# @Author : Keginx
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
