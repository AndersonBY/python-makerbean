# -*- coding: utf-8 -*-
# @Author: Anderson
# @Date:   2019-11-11 17:42:18
# @Last Modified by:   Anderson
# @Last Modified time: 2020-12-25 11:47:59
from .WebCrawlerBot import WebCrawlerBot
from .ExcelBot import ExcelBot
from .DataAnalysisBot import DataAnalysisBot
from .PDFBot import PDFBot
from .WordBot import WordBot


爬虫机器人 = web_crawler_bot = WebCrawlerBot()
表格机器人 = excel_bot = ExcelBot()
数据机器人 = data_analysis_bot = DataAnalysisBot()
PDF机器人 = pdf_bot = PDFBot()
文档机器人 = word_bot = WordBot()
