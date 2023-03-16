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
    if selenium:
        b = browser.find_element(By.NAME, 'up-btn up-btn-secondary up-btn-block-sm mb-0')
        b.click()
    browser.get(url)

    time.sleep(1)

    html = browser.page_source
    return html


# 从网页中提取数据
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 提取职位名称和链接
    jobs = {}
    # job_list = soup.find('ul', class_='p-0')
    for idx, li in enumerate(soup.find_all('div', class_='job-tile-wrapper')):
        print("job:", idx)
        job = {}
        name_node = li.find('a')
        if not name_node:
            continue
        job['name'] = name_node.text
        job['link'] = 'https://www.upwork.com' + li.find('a')['href']
        read_ok = add_more_info(job['link'], job)
        if read_ok:
            jobs[idx] = job
    return jobs


def add_more_info(url, info_map):
    info_html = get_page_new(url, selenium=False)
    soup = BeautifulSoup(info_html, 'html.parser')
    try:
        description_node = soup.find('div', class_='job-description break mb-0').find('div')
        info_map["description"] = description_node.text if description_node else None

        date_node = soup.find('div', class_='d-inline-block mr-10').find('span', class_='inline')
        info_map["date"] = date_node.text if date_node else None

        location_node = soup.find('div', class_='mt-20 d-flex align-items-center location-restriction').find('span', class_='vertical-align-middle')
        info_map["job_location"] = location_node.text.strip() if location_node else None

        info_node = soup.find('ul', class_='cfe-ui-job-features p-0 fluid-layout-md')
        for idx, li in enumerate(info_node.find_all('li')):
            info = li.find('strong').text.strip()

            if li.find('div', attrs={"data-cy": 'clock-hourly'}):
                info_map["work_hour"] = info
            elif li.find('div', attrs={"data-cy": 'calendar-up-to-6months'}):
                info_map["job_duration"] = info
            elif li.find('div', attrs={"data-cy": 'expertise'}):
                info_map["exp_level"] = info
            elif li.find('div', attrs={"data-cy": 'clock-timelog'}):
                info_map["pay"] = info
            elif li.find('div', attrs={"data-cy": 'local'}):
                info_map["job_type"] = info
            elif li.find('div', attrs={"data-cy": 'briefcase-outlined'}):
                info_map["project_type"] = info
            elif li.find('div', attrs={"data-cy": 'fixed-price'}):
                info_map["project_type"] = info

        tag_node = soup.find('div', class_='mt-20 group')
        info_map["tags"] = "".join([span.text for span in tag_node.find_all('span', class_="cfe-ui-job-skill up-skill-badge disabled m-0-left m-0-top m-xs-bottom")])

        info_map["proposals"] = soup.find('li', class_="d-flex d-md-block justify-space-between").find('div', class_='d-md-none').find('span').text
        info_map["client_location"] = soup.find('ul', class_="list-unstyled cfe-ui-job-about-client-visitor mb-0").find('li', attrs={'data-qa': 'client-location'}).find('strong').text
    except Exception as e:
        print(f"[{url}] error: {e}")
        return False

    return True


# 保存数据到文件
def save_data(data, page, save_dir):
    with open(f'{save_dir}/page{page}.json', "w") as f:
        f.write(json.dumps(data, indent=4))


def json2txt(json_path, page, save_dir):
    with open(json_path) as f:
        data = json.loads(f.read())
    with open(f'{save_dir}/page{page}.txt', 'w') as f:
        f.write(f"total jobs: {len(data)}")
        for idx, job in data.items():
            print("save:", idx)
            f.write("name:" + job.get('name') + '\n')
            f.write("date:" + job.get('date') + '\n')
            f.write("job_location:" + job.get('job_location') + '\n')
            f.write("client_location:" + job.get('client_location') + '\n')
            f.write("tags:" + job.get('tags') + '\n')
            f.write("work_hour:" + job.get('work_hour', "None") + '\n')
            f.write("job_duration:" + job.get('job_duration', "None") + '\n')
            f.write("exp_level:" + job.get('exp_level', "None") + '\n')
            f.write("pay:" + job.get('pay', "None") + '\n')
            f.write("job_type:" + job.get('job_type', "None") + '\n')
            f.write("project_type:" + job.get('project_type', "None") + '\n')
            f.write("description:" + job.get('description') + '\n')
            f.write("proposals:" + job.get('proposals') + '\n')
            f.write("link:" + job.get('link') + '\n\n')




def main(save_dir, category):
    for p in range(1, 2):
        print("page", p)
        # 要爬取的网页地址 category=Computer&IT,remote=100% remote work,schedule=full-time
        url = f"https://www.upwork.com/freelance-jobs/{category}/"

        # 获取网页内容
        html = get_page_new(url)

        # 提取数据
        jobs = parse_page(html)

        # 保存数据
        save_data(jobs, p, save_dir)

        print("done")

        time.sleep(2)


if __name__ == '__main__':
    category = "javascript"
    dir_path = f"upwork/{category}/{date_str}"
    os.makedirs(dir_path, exist_ok=True)

    main(dir_path, category=category)

    json_path = os.path.join(dir_path, "page1.json")
    json2txt(json_path, '1', dir_path)
