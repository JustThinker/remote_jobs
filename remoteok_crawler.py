import os
import time
from datetime import date
import requests

import json
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

date_str = str(date.today())
category_map = {"computer&it": '11'}
schedule_map = {"fulltime": "Full-Time"}
remote_map = {"allremote": "All+Telecommuting"}

stop_idx = 30


# 获取网页内容
def get_page(url):
    # 如果不需要使用代理服务器，可以删除下面的代码
    proxies = {
        'http': '127.0.0.1:7890',
        'https': '127.0.0.1:7890',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }
    response = requests.get(url, proxies=proxies, headers=headers)
    return response.text


def get_page_new(url, selenium=True):
    browser = uc.Chrome()
    browser.get(url)
    if selenium:
        for _ in range(10):
            browser.execute_script("window.scrollBy(0,2000);")
            time.sleep(2)
    time.sleep(2)

    html = browser.page_source
    browser.quit()
    return html


# 从网页中提取数据
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 提取职位名称和链接
    jobs = {}
    # job_list = soup.find('ul', class_='p-0')
    for idx, tr in enumerate(soup.find_all('tr', attrs={'data-offset': True})):
        if idx > stop_idx:
            break
        print("job:", idx)
        job = {}
        for key, value in tr.attrs.items():
            if key == "data-href":
                job['href'] = 'https://www.remoteok.com' + value
            if key == "data-company":
                job['company'] = value
        read_ok = add_more_info(job['href'], job)
        if read_ok:
            jobs[idx] = job
    return jobs


def add_more_info(url, info_map):
    info_html = get_page_new(url, selenium=False)
    soup = BeautifulSoup(info_html, 'html.parser')
    try:
        title_tr = soup.find('tr', attrs={'data-offset': True})

        title_td = title_tr.find('td', class_='company position company_and_position')
        info_map['name'] = title_td.find('h2').text.strip()
        for idx, div in enumerate(title_td.find_all('div', class_='location')):
            if idx == 0:
                info_map['location'] = div.text.strip()
            else:
                info_map['pay'] = div.text.strip()

        tags_td = title_tr.find('td', class_='tags')
        tags = []
        for idx, a in enumerate(tags_td.find_all('a', class_='no-border tooltip-set action-add-tag')):
            tags.append(a.find('h3').text.strip())
        info_map['tags'] = ";".join(tags)

        time_td = title_tr.find('td', class_='time')
        info_map['day'] = time_td.find('time').text.strip()

        description_tr = soup.find('tr', attrs={'data-id': True, 'data-offset': False})
        description = description_tr.find('div', class_='html')
        if description is None:
            description = description_tr.find('div', class_='markdown')
        if description.find('div'):
            description = description.find('div')
        descriptions = []
        for t in description.descendants:
            name = t.name
            strs = t.string
            if name and strs and strs not in descriptions:
                descriptions.append(t.string.strip())
        info_map['description'] = "\n".join(descriptions)

    except Exception as e:
        print(f"[{url}] error: {e}")
        return False

    return True


# 保存数据到文件
def save_data(data, save_dir):
    with open(f'{save_dir}/jobs.json', "w") as f:
        f.write(json.dumps(data, indent=4))


def json2txt(json_path, save_dir):
    with open(json_path) as f:
        data = json.loads(f.read())
    with open(f'{save_dir}/jobs.txt', 'w') as f:
        f.write(f"total jobs: {len(data)}\n")
        for idx, job in data.items():
            print("save:", idx)
            f.write("name:" + job.get('name') + '\n')
            f.write("day:" + job.get('day') + '\n')
            f.write("location:" + job.get('location') + '\n')
            f.write("pay:" + job.get('pay') + '\n')
            f.write("tags:" + job.get('tags') + '\n')
            f.write("company:" + job.get('company') + '\n')
            f.write("description:" + job.get('description') + '\n')
            f.write("href:" + job.get('href') + '\n\n')


def main(save_dir, category):
    # 要爬取的网页地址 category=Computer&IT,remote=100% remote work,schedule=full-time
    url = f"https://remoteok.com/remote-{category}-jobs?order_by=salary"

    # 获取网页内容
    html = get_page_new(url)

    # 提取数据
    jobs = parse_page(html)

    # 保存数据
    save_data(jobs, save_dir)

    print("done")

    time.sleep(2)


if __name__ == '__main__':
    category = "react"
    dir_path = f"remoteok/{category}/{date_str}"
    os.makedirs(dir_path, exist_ok=True)

    main(dir_path, category=category)

    json_path = os.path.join(dir_path, "jobs.json")
    json2txt(json_path,  dir_path)
