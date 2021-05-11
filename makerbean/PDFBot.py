# -*- coding: utf-8 -*-
# @Author: ander
# @Date:   2020-12-22 16:19:51
# @Last Modified by:   ander
# @Last Modified time: 2020-12-22 16:25:49
import pdfplumber
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import os.path
from .utilities import mkdir


class PDFBot(object):
    """docstring for ExcelBot"""

    def __init__(self):
        self.page_num = 0

    def open(self, file_path):
        self.filename, _ = os.path.splitext(os.path.basename(file_path))
        self.pdf = pdfplumber.open(file_path)
        self.pdf_reader = PdfFileReader(file_path)
        self.page_num = self.pdf_reader.getNumPages()

    def get_text(self, page):
        pdf_page = self.pdf.pages[page]
        return pdf_page.extract_text()

    def split(self, page, folder):
        mkdir(folder)
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(self.pdf_reader.getPage(page))
        with open(os.path.join(folder, f"{self.filename}-p{page}.pdf"), "wb") as out:
            pdf_writer.write(out)

    def merge(self, pdfs, merged_name):
        merger = PdfFileMerger()
        for pdf in pdfs:
            merger.append(PdfFileReader(pdf))
        merger.write(f"{merged_name}.pdf")
