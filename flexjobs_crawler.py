import os
import time

import requests
from datetime import date
from bs4 import BeautifulSoup

date_str = str(date.today())
category_map = {"computer&it": '11'}
schedule_map = {"fulltime": "Full-Time"}
remote_map = {"allremote": "All+Telecommuting"}


# 获取网页内容
def get_page(url):
    # 如果不需要使用代理服务器，可以删除下面的代码
    proxies = {
        'http': '127.0.0.1:7890',
        'https': '127.0.0.1:7890',
    }
    response = requests.get(url, proxies=proxies)
    return response.text


# 从网页中提取数据
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 提取职位名称和链接
    jobs = []
    job_list = soup.find('ul', class_='p-0')
    for li in job_list.find_all('li'):
        job = {}
        job['name'] = li.find('a').text
        job['location'] = li.find('div', class_='col pe-0 job-locations text-truncate').text.strip()
        job['description'] = li.find('div', class_='job-description').text.strip()
        job['date'] = li.find('div', class_='job-age').text.replace("New!\n", "").strip()
        accolades = li.find('div', class_='job-accolades mt-2')
        job['accolades'] = str(len(accolades.find_all('img'))) if accolades else '0'
        job['link'] = 'https://www.flexjobs.com' + li.find('a')['href']
        jobs.append(job)
    return jobs


def get_company(html):
    pass


# 保存数据到文件
def save_data(data, page, save_dir):
    with open(f'{save_dir}/page{page}.txt', 'w') as f:
        for job in data:
            f.write("name:" + job['name'] + '\n')
            f.write("date:" + job['date'] + '\n')
            f.write("location:" + job['location'] + '\n')
            f.write("accolades:" + job['accolades'] + '\n')
            f.write("description:" + job['description'] + '\n')
            f.write("link:" + job['link'] + '\n\n')


def main(save_dir, params):
    for p in range(1, 51):
        print("page", p)
        # 要爬取的网页地址 category=Computer&IT,remote=100% remote work,schedule=full-time
        url = f'https://www.flexjobs.com/search?category%5B%5D={params[0]}&schedule%5B%5D={params[1]}&search=&tele_level%5B%5D={params[2]}&page={p}'
        # url = 'https://www.flexjobs.com/search?search=python'

        # 获取网页内容
        html = get_page(url)

        # 提取数据
        jobs = parse_page(html)

        # 保存数据
        save_data(jobs, p, save_dir)

        print("done")

        time.sleep(2)


if __name__ == '__main__':
    category = "computer&it"
    category_param = category_map.get(category)
    schedule = "fulltime"
    schedule_param = schedule_map.get(schedule)
    remote = "allremote"
    remote_param = remote_map.get(remote)
    dir_path = f"flexjobs/{category}/{schedule}/{remote}/{date_str}"
    os.makedirs(dir_path, exist_ok=True)
    main(dir_path, params=(category_param, schedule_param, remote_param))
