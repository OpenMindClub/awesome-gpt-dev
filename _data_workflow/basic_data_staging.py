import requests
import os,sys,time
from bs4 import BeautifulSoup
import json
import re
import pandas as pd
import datetime
from collections import defaultdict
import configparser
import pymongo
from tqdm import tqdm

# 运行环境初始化
os.environ["http_proxy"] = "http://127.0.0.1:1088"
os.environ["https_proxy"] = "http://127.0.0.1:1088"

# 接口数据mapping
def extract_info(item):
    owner, repo = item['hl_name'].split('/')
    access_url = f"https://github.com/{owner}/{repo}"
    description = item['hl_trunc_description']
    is_organization = item['owned_by_organization']
    language = item['language']
    stars = item['followers']
    topics = item['topics']
    
    return {
        'owner': owner,
        'repo':repo,
        'access_url':access_url,
        'description': description,
        'is_organization': is_organization,
        'language': language,
        'stars': stars,
        'topics': topics
    }

# 处理 mongo 连接
class mongo_connector:
    def __init__(self, server_profiles):
        self.mongo_host = ''
        self.mongo_database = ''
        self.mongo_client = ''
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(minutes=40)
        
        self.server_profiles = server_profiles
    
    def get_config(self):
        """读取配置文件获取相关信息"""
        print("连接环境：{}".format(self.server_profiles))
        cf = configparser.ConfigParser()
        cf.read("./config.ini")
        
        self.mongo_host = 'mongodb://{}:{}/'.format(cf.get(self.server_profiles, 'mongo_host'), cf.get(self.server_profiles, 'mongo_port'))
        self.mongo_database = cf.get(self.server_profiles, 'mongo_database')
        self.mongo_client = pymongo.MongoClient(self.mongo_host)[self.mongo_database]

def web_advsearch(base_url):
    project_data = []
    page = 1
    while True:
        print(f"正在爬取第{page}页")
        url = base_url + str(page)

        headers = {
        'authority': 'github.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': '_octo=GH1.1.1068890711.1676342497; _device_id=0e89bed47f11713a3508cf01de58d412; user_session=XY71LMi4QgZiSOqiDQQWM-yHqkS6bMeNK4JL8L5WRnb2QFUx; __Host-user_session_same_site=XY71LMi4QgZiSOqiDQQWM-yHqkS6bMeNK4JL8L5WRnb2QFUx; logged_in=yes; dotcom_user=JanusChoi; color_mode=%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; preferred_color_mode=dark; tz=Asia%2FShanghai; fileTreeExpanded=true; has_recent_activity=1; _gh_sess=o%2BZvo7NbgYElNo%2F5HDbJdknFAr1TYnxWbgNpbOYxh8%2Bvq9RbCrW%2FEZ9VCHBOD9C1FWevXB3vswnfBe%2FJ0jkBQvmc0e6jmewuqVNNrRRm3DU%2B%2B1naRyQrPkH3A4VEMxorQBY%2B0LXo9ISBzLLkfd5u73x7Hx3P6ioXVyhEz6s2fCy%2Fex6znzmah4MdJdDc8IiQLYmfa4McCy1QBdrtin23G%2Fs54BL5pxkfSppkE6WS953sqOLKWwYZd4wlD%2B1Y2QXk6837ISBEAoz2%2B8OUsjOGgS9HsTGYwCZt%2BCCj%2B6emdnBMeFtGM3Tg1ZjZSK%2BNalzVt%2FPPlN%2BtvISbkZjPgb3vFjWLgARHEZZS7IeLSIIQ8NX95heRSUYktgcnhwTA8Kc5tZDEkeOabLV6oYuzKDQ0UwUA7Ef7j2%2BJbvZCpyKMUhOcNTGKTPqzpEJbMAoVxRajYyZKuDnWHGEJB4NpMUeGTgLdbgNjoivaSGFSAEygy4jv--KVd37YSkwHiqBhv2--Uo3eML2hajqzmTCfohyEug%3D%3D',
        'if-none-match': 'W/"866a4073e03db5ba881df79c53a090be"',
        'referer': 'https://github.com/search/advanced',
        'sec-ch-ua': '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            embedded_data = soup.find('script', {'type': 'application/json', 'data-target': 'react-app.embeddedData'})
            data = json.loads(embedded_data.string)
            search_results = data['payload']['results']
            items = search_results
            if items == []:
                break
            for item in items:
                project_info = extract_info(item)
                project_data.append(project_info)
        else:
            print(f"Failed to fetch data: {response.status_code}, {response.reason}, {response.url}")
        time.sleep(0.1)
        page += 1
    return project_data

# 构造查询url
def construct_url(created, stars, label):
    return "https://github.com/search?q=created%3A%3E{}+stars{}+label%3A{}&type=Repositories&ref=advsearch&l=&l=&p=".format(created, stars, label)

# 提取项目所有commits数据，按天汇总
def get_repo_commits(owner, repo):
    commits_by_date = defaultdict(int)
    base_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "token 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"
    }
    page = 1

    while True:
        url = f"{base_url}?page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}, {response.reason}, {response.url}")
            break

        data = json.loads(response.text)
        if not data:  # If the response data is empty, we've reached the end of the commits list
            break

        for commit in data:
            date_str = commit['commit']['author']['date']
            date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').date()
            commits_by_date[date] += 1

        page += 1
    print(f"Found {len(commits_by_date)} commit dates for {owner}/{repo}.")

    return dict(commits_by_date)

# 提取项目所有stars数据，按天汇总
def get_repo_stars(owner, repo, input_date, end_page):
    stars_by_date = defaultdict(int)
    base_url = f"https://api.github.com/repos/{owner}/{repo}/stargazers?per_page=100"
    headers = {
      'Accept': 'application/vnd.github.v3.star+json',
      'Authorization': 'Bearer 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',
      'X-GitHub-Api-Version': '2022-11-28'
    }
    while True:
        if end_page > 400:
            break
        url = f"{base_url}&page={end_page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}, {response.reason}, {response.url}")
            break

        data = json.loads(response.text)
        if not data:
            break

        for stars in data:
            date_str = stars['starred_at']
            date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').date()
            stars_by_date[date] += 1
            
        if date > input_date:
            break
        elif date <= input_date:
            end_page += 1

    return end_page, stars_by_date[input_date]

if __name__ == '__main__':
    print("start to sync github project data...")

    # get input parameters
    env = sys.argv[1] # 环境 dev/uat/prd
    sync_time = datetime.datetime.now().strftime("%Y-%m-%d_%H|%M|%S")
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mongo_conn = mongo_connector(env)
    mongo_conn.get_config()
    mg_stage = mongo_conn.mongo_client
    tb_dim_github_project = mg_stage['dim_github_project']
    tb_fact_github_project = mg_stage['fact_github_project']
    # tb_dim_github_project.drop()
    # tb_fact_github_project.drop()
    print("start to sync top class...")

    # top_class 项目信息抓取
    created = '2023-03-01'
    stars = '%3A%3E10000'
    label = 'GPT'
    url = construct_url(created, stars, label)
    # top_class_projects = web_advsearch(url)
    # tb_dim_github_project.insert_many(top_class_projects)
    print("top_class_projects inserted successfully!")
    print("start to sync high class...")

    # high_class 项目信息抓取
    created = '2023-03-01'
    stars = '%3A3000..10000'
    label = 'GPT'
    url = construct_url(created, stars, label)
    # top_class_projects = web_advsearch(url)
    # tb_dim_github_project.insert_many(top_class_projects)
    print("high_class_projects inserted successfully!")
    print("start to sync mid class...")

    # mid_class 项目信息抓取
    created = '2023-03-01'
    stars = '%3A1000..3000'
    label = 'GPT'
    url = construct_url(created, stars, label)
    # top_class_projects = web_advsearch(url)
    # tb_dim_github_project.insert_many(top_class_projects)
    print("mid_class_projects inserted successfully!")
    print("start to get commits & stars history")

    # 抓取所有项目历史数据
    for project in tb_dim_github_project.find({'owner':'crablang', 'repo':'crab'}):
        owner = project['owner']
        repo = project['repo']
        commits_by_date = get_repo_commits(owner, repo) # 一次性获取所有commits数据
        project_commits = []
        # 按时间顺序整理
        for date, count in commits_by_date.items():
            project_commits.append({'repo':repo, 'date':date, 'commits':count})
        df_project_commits = pd.DataFrame(project_commits)
        sorted_df_project_commits = df_project_commits.sort_values(by='date', ascending=True)
        # 按时间顺序获取所有stars数据
        end_page = 1
        project_history = []
        for index, row in tqdm(sorted_df_project_commits.iterrows()):
            end_page, stars_by_date = get_repo_stars(owner, repo, row['date'], end_page)
            project_history.append({'owner':owner, 'repo':repo, 'tdate':str(row['date']),'commits':row['commits'], 'stars':stars_by_date})

        # 更新tb_dim_github_project对应repo的最近一次stars采集的页数
        tb_dim_github_project.update_one({'owner':owner, 'repo':repo}, {'$set':{'end_page':end_page}})
        # 插入tb_fact_github_project
        tb_fact_github_project.insert_many(project_history)
        print(f"{owner}/{repo} commits & stars collect successfully!")
    print("all projects facts inserted successfully!")
    