# -*- coding: utf-8 -*-
# @Author: ander
# @Date:   2020-12-22 16:13:58
# @Last Modified by:   Anderson
# @Last Modified time: 2021-10-01 01:03:30
import json
import time
from copy import copy
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .utilities import validate_title, mkdir
import os.path


class WebCrawlerBot(object):
    """docstring for WebCrawlerBot"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        self.weibo_hot_list = []
        self.liepin_urls = {}
        self.session = requests.Session()
        self.抓取猎聘 = self.get_liepin
        self.抓取论文 = self.get_arxiv
        self.抓取花瓣 = self.get_huaban
        self.抓取微博热搜 = self.get_weibo_hot
        self.下载图片 = self.download_image

    def set_cookie(self, cookie):
        self.headers["cookie"] = cookie

    def get_weibo_hot(self, index):
        # 列表第一位不是正常内容
        index += 1
        if not self.weibo_hot_list:
            base_url = "https://s.weibo.com/top/summary"
            req = requests.get(base_url, headers=self.headers)
            soup = BeautifulSoup(req.text, "lxml")
            today_hot = soup.select("#pl_top_realtimehot tr")[1:]
            self.weibo_hot_list = copy(today_hot)
        item = self.weibo_hot_list[index]
        title = item.select(".td-02 a")[0].text.strip()
        hot_count = int(item.select(".td-02 span")[0].text.strip())
        url = item.select(".td-02 a")[0].get("href")
        if "javascript" in url:
            url = item.select(".td-02 a")[0].get("href_to")
        url = f"https://s.weibo.com{url}"

        # Get detail info
        req = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(req.text, "lxml")
        author = soup.select(".card-wrap .content .info .name")[0].text.strip()
        content = soup.select(".card-wrap .content .txt")[0].text.strip()
        return [hot_count, title, author, content, url]

    def get_liepin(self, keyword, start_page, end_page=None):
        if keyword not in self.liepin_urls:
            url = f'https://www.liepin.com/zhaopin/?key={quote_plus(keyword)}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
            }
            req = requests.get(url, headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            inputs = soup.select('#filter-options-form input')
            head_id = inputs[0]['value']
            ck_id = inputs[1]['value']
            self.liepin_urls[keyword] = f"https://www.liepin.com/zhaopin/?headId={head_id}&ckId={ck_id}&key={quote_plus(keyword)}&currentPage="
        if end_page is None:
            end_page = start_page + 1
        results = []
        for page in range(start_page, end_page):
            time.sleep(1)
            url = self.liepin_urls[keyword] + str(page)
            req = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(req.text, "lxml")
            for item in soup.select(".job-list-item"):
                job_name = item.select_one(".job-title-box>.ellipsis-1").text.strip()
                job_company = item.select_one(".company-name").text.strip()
                company_tags = item.select_one(".company-tags-box").text.strip()
                job_salary = item.select_one(".job-salary").text.strip()
                if job_salary == "面议":
                    annual_salary = -1
                else:
                    if "-" in job_salary:
                        min_salary = int(job_salary[: job_salary.index("-")])
                        if "k" in job_salary:
                            max_salary = int(
                                job_salary[
                                    job_salary.index("-") + 1: job_salary.index("k")
                                ]
                            )
                        elif "万" in job_salary:
                            max_salary = (
                                int(
                                    job_salary[
                                        job_salary.index("-")
                                        + 1: job_salary.index("万")
                                    ]
                                )
                                * 10
                            )
                        else:
                            max_salary = min_salary
                        months = (
                            int(job_salary[job_salary.index("·") + 1: -1])
                            if "·" in job_salary
                            else 12
                        )
                        annual_salary = (min_salary + max_salary) / 2 * months * 1000
                    else:
                        if "k" in job_salary:
                            monthly_salary = int(job_salary.split("k")[0])
                        elif "万" in job_salary:
                            monthly_salary = (
                                int(
                                    job_salary[
                                        job_salary.index("-")
                                        + 1: job_salary.index("万")
                                    ]
                                )
                                * 10
                            )
                        else:
                            monthly_salary = 0
                        months = (
                            int(job_salary[job_salary.index("·") + 1 : -1])
                            if "·" in job_salary
                            else 12
                        )
                        annual_salary = monthly_salary * months * 1000
                job_area = item.select_one(".job-dq-box .ellipsis-1").text.strip()
                job_edu = item.select(".job-labels-box .labels-tag")[0].text.strip()
                job_experience = item.select(".job-labels-box .labels-tag")[-1].text.strip()
                results.append(
                    [
                        job_name,
                        job_company,
                        company_tags,
                        job_salary,
                        annual_salary,
                        job_area,
                        job_edu,
                        job_experience,
                    ]
                )
        return results

    def get_huaban(self, keyword, page, key="k4rwsxf5"):
        url = f"https://huaban.com/search/?q={quote_plus(keyword)}&type=pins&{key}&page={page+1}&per_page=20&wfl=1"
        req = requests.get(url, headers=self.headers)
        source = str(req.text)
        start_index = source.index('app.page["pins"] = ') + len('app.page["pins"] = ')
        end_index = start_index + source[start_index:].index('app.page["page"]')
        results = []
        for img in json.loads(source[start_index:end_index].strip()[:-1]):
            results.append(
                {
                    "url": f"https://hbimg.huabanimg.com/{img['file']['key']}",
                    "name": validate_title(
                        f"{img['board']['title']}-{img['pin_id']}.jpg"
                    ),
                }
            )

        return results

    def get_arxiv(self, keyword, page):
        url = f"https://arxiv.org/search/?query={quote_plus(keyword)}&searchtype=all&source=header&order=-announced_date_first&size=50&abstracts=show&start={50*page}"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "lxml")
        results = soup.select(".arxiv-result")
        output_results = []
        for result in results:
            output_result = {}
            output_result["title"] = result.select(".title")[0].text.strip()
            authors = []
            for author in result.select(".authors a"):
                authors.append(author.text.strip())
            output_result["authors"] = authors
            output_result["abstract"] = (
                result.select(".abstract-full")[0].text.replace("△ Less", "").strip()
            )
            if result.find("a", string="pdf"):
                output_result["pdf"] = result.find("a", string="pdf").attrs["href"]
            else:
                output_result["pdf"] = ""

            output_results.append(output_result)

        return output_results.copy()

    def download_image(self, url, filename, folder):
        mkdir(folder)
        req = requests.get(url)
        with open(os.path.join(folder, f"{validate_title(filename)}"), "wb") as f:
            f.write(req.content)
