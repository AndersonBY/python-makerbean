# -*- coding: utf-8 -*-
# @Author: ander
# @Date:   2020-12-22 16:19:12
# @Last Modified by:   ander
# @Last Modified time: 2020-12-22 16:19:27
from docx import Document


class WordBot(object):
	"""docstring for WordBot"""

	def __init__(self):
		self.doc = Document()

	def set_paragraph(self, index, text):
		if index < len(self.doc.paragraphs):
			self.doc.paragraphs[index].text = str(text)
			return True
		else:
			return False

	def get_paragraph(self, index):
		if index < len(self.doc.paragraphs):
			return str(self.doc.paragraphs[index].text)
		else:
			return ''

	@property
	def paragraphs(self):
		return [str(p.text) for p in self.doc.paragraphs]

	def clear(self):
		self.doc = Document()

	def open(self, filename):
		self.doc = Document(filename)

	def save(self, filename):
		if not filename:
			filename = 'tmp'
		self.doc.save(f'{filename}.docx')
