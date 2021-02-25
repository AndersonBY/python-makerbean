# -*- coding: utf-8 -*-
# @Author: ander
# @Date:   2020-12-22 16:21:12
# @Last Modified by:   ander
# @Last Modified time: 2021-02-25 15:37:31
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import WordCloud
from pyecharts.charts import Map3D
from pyecharts.globals import ChartType
from pyecharts.commons.utils import JsCode
from copy import copy
from collections import Counter


class _MyDataFrame:

	def __init__(self, data):
		self.df = data
		self.列名称 = self.column_names
		self.提取一列数据 = self.get_col
		self.设定一列数据 = self.set_col
		self.文字筛选 = self.filter_words
		self.合并统计 = self.value_counts

	def __str__(self):
		return str(self.df)

	def set_data(self, data):
		self.df = data

	@property
	def column_names(self):
		return self.df.columns.values.tolist()

	def get_col(self, col):
		return self.df[col]

	def set_col(self, col, data):
		if self.df[col].size != len(data):
			raise RuntimeError(f'传入数据长度为{len(data)}，本列数据长度为{self.df[col].size}，数据长度不一致，无法设定！')
		else:
			new_df = self.df.copy()
			new_df[col] = data
			return _MyDataFrame(new_df)

	def filter_words(self, col, value):
		return _MyDataFrame(self.df[self.df[col] == value])

	def value_counts(self, col):
		return self.df[col].value_counts()

	def 数据筛选(self, col, 最小值=float('-inf'), 最大值=float('inf')):
		return self.filter_numbers(col, min_value=最小值, max_value=最大值)

	def 文字裁剪(self, col, 截止字符=''):
		return self.cut_words(col, stop_words=截止字符)

	def filter_numbers(self, col, min_value=float('-inf'), max_value=float('inf')):
		return _MyDataFrame(self.df[(self.df[col] >= min_value) & (self.df[col] <= max_value)])

	def cut_words(self, col, stop_words=''):
		def cut_str(x):
			final_result = x
			for stop_letter in stop_words:
				cut_result = x[:x.index(stop_letter) + len(stop_letter)] if stop_letter in x else x
				if len(cut_result) < len(final_result):
					final_result = cut_result
			return final_result

		if isinstance(stop_words, str):
			cut_data = self.df.copy()
			cut_data = cut_data[col].apply(
				lambda x: x[:x.index(stop_words) + 1] if stop_words in x else x
			)
			return _MyDataFrame(cut_data)
		elif isinstance(stop_words, list):
			cut_data = self.df.copy()
			cut_data[col] = cut_data[col].apply(cut_str)
			return _MyDataFrame(cut_data)

	def 删除前缀(self, col, 前缀=''):
		return self.remove_prefix(col, 前缀)

	def remove_prefix(self, col, prefix):
		new_df = self.df.copy()
		new_df[col] = new_df.df[col].str.lstrip(prefix)
		return _MyDataFrame(new_df)


class DataAnalysisBot(object):
	"""docstring for DataAnalysisBot"""
	def __init__(self):
		self.data = []
		self.分析词语频次 = self.get_word_frequency
		self.生成词云图 = self.generate_word_cloud
		self.生成3D地图 = self.generate_3d_map
		self.加载内置数据 = self.load_builtin_data

	def load_builtin_data(self, name):
		if name == '商品订单数据':
			from .data import orders_data
			data = _MyDataFrame(pd.DataFrame(orders_data))
			return data
		elif name == '用户信息数据':
			from .data import user_info
			data = _MyDataFrame(pd.DataFrame(user_info))
			return data

	def set_data(self, data):
		self.data = copy(data)

	def get_word_frequency(self, data, count=20):
		import jieba
		from .stop_words import stop_words
		word_frequency = []
		words = ''
		if isinstance(data, str):
			words = data
		elif isinstance(data, list):
			words = '\n'.join([str(item) for item in data])

		punct = set(u''' #:!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
		﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
		々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
		︽︿﹁﹃﹙﹛﹝（｛“‘-—_…@~/\\''')

		words_cut = list(filter(lambda x: x not in punct, jieba.lcut(words)))
		words_cut = list(filter(lambda x: x not in stop_words, words_cut))
		word_frequency = Counter(words_cut).most_common(count)

		return copy(word_frequency)

	def generate_word_cloud(self, data):
		wordcloud = WordCloud()
		wordcloud.add("", data, word_size_range=[20, 100])
		wordcloud.render('word_cloud.html')

	def generate_bar(self, x_axis, y_axis):
		bar = Bar(
			init_opts=opts.InitOpts(
				width="1280px",
				height="720px"))
		bar.add_xaxis(x_axis)
		bar.add_yaxis("", y_axis)
		bar.set_global_opts(
			xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=10)))
		bar.render('bar.html')

	def generate_3d_map(self, provinces_data):
		map_3d = Map3D(
			init_opts=opts.InitOpts(
				width="1280px",
				height="720px"))
		map_3d.add_schema(
			itemstyle_opts=opts.ItemStyleOpts(
				color="#172eb2",
				opacity=1,
				border_width=0.8,
				border_color="rgb(76, 96, 255)",
			),
			map3d_label=opts.Map3DLabelOpts(
				is_show=False,
				formatter=JsCode("function(data){return data.name + " " + data.value[2];}"),
			),
			emphasis_label_opts=opts.LabelOpts(
				is_show=False,
				color="#fff",
				font_size=10,
				background_color="rgba(242, 149, 128, 0)",
			),
			light_opts=opts.Map3DLightOpts(
				main_color="#fff",
				main_intensity=1.2,
				main_shadow_quality="high",
				is_main_shadow=True,
				main_beta=10,
				ambient_intensity=0.3,
			),
			is_show_ground=True,
			ground_color="#FFF",
		)

		map_3d_data = []
		from .data import provinces_coordinates
		for item in provinces_data.items():
			province_data = (
				item[0],
				[*provinces_coordinates[item[0]], item[1]]
			)
			map_3d_data.append(province_data)

		map_3d.add(
			series_name="Data",
			data_pair=map_3d_data,
			type_=ChartType.BAR3D,
			bar_size=1,
			itemstyle_opts=opts.ItemStyleOpts(
				color="rgb(173, 212, 217)"
			),
			shading="realistic",
			label_opts=opts.LabelOpts(
				is_show=False,
				formatter=JsCode("function(data){return data.name + ' ' + data.value[2];}"),
			),
		)
		map_3d.set_global_opts(title_opts=opts.TitleOpts(title="3D Map"))
		map_3d.render("map3d_with_bar3d.html")
