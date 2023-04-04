from bs4 import BeautifulSoup
import requests
import time
import re
import random
import json


def clean_code(code):
    # clean comments
    comment = re.compile(r"/\*\*.*\*/", re.S)
    comment1 = re.compile(r"//.*\n")
    solution_split = re.compile(r"//.解法.*\n")

    # how many solutions?
    solution_num = re.compile(r"//.解法.")
    s_num = solution_num.findall(code)
    if len(s_num) == 0:
        s = code.replace('package leetcode', '').strip()
        s = comment.sub('', s)
        s = [comment1.sub('', s)]
    else:
        s = solution_split.split(code)[1:]
        s = [comment.sub('', ss) for ss in s]
        s = [comment1.sub('', ss) for ss in s]

    s = [re.sub(r"\s+", ' ', ss) for ss in s]
    return s


def get_code_info(url):
    html = requests.get(url)
    html.encoding = 'utf-8'

    bs = BeautifulSoup(html.text, "html.parser")

    title = bs.find('h1').next_element.text
    title = re.sub(r"\s+", ' ', title).strip()

    article_cont = bs.find('article', class_='markdown').contents

    index = {'Example': None, '代码': None}
    for i,a in enumerate(article_cont):
        if a.name == 'h2' and a.get('id')=="题目":
            index["题目"] = i
        if a.name =='p' and a.next_element.name == 'strong':
            if index['Example'] is None:
                index['Example'] = i

        if a.name == 'h2' and a.get('id') == '题目大意':
            index['题目大意'] = i
        if a.name == 'h2' and a.get('id') == '解题思路':
            index['解题思路'] = i
        if a.name == 'h2' and a.get('id') == '代码':
            if index['代码'] is None:
                index['代码'] = i

    # get the nl
    nl_en = article_cont[index['题目']+1: index['Example']]
    nl_en = [re.sub(r"\s+", ' ', n.get_text()) for n in nl_en]

    # get the examples

    if index['Example'] is not None:
        examples = article_cont[index['Example']+1: index['题目大意']]
        examples = [re.sub(r"\s+", ' ', e.next_element.text) for e in examples if e.name == 'pre']
    else:
        examples = None

    # get the nl_cn
    nl_meaning_cn = article_cont[index['题目大意']+1: index['解题思路']]
    nl_meaning_cn = [re.sub(r"\s+", ' ', n.text) for n in nl_meaning_cn]

    # get the idea
    idea = article_cont[index['解题思路']+1: index['代码']]
    idea = [re.sub(r"\s+", ' ', i.get_text()) for i in idea]

    # get the code
    code = bs.find_all('code', class_='language-go')
    if len(code) == 0:
        code = None
    else:
        code = code[-1].get_text()
        code = clean_code(code)

    data = {
        'title': title,
        "nl": nl_en,
        "examples": examples,
        "nl_meaning_cn": nl_meaning_cn,
        "idea": idea,
        "code": code
    }

    flag = True
    for v in data.values():
        if v is None:
            flag = False

    if not flag:
        print(f'the url example is not exist or wrong !  {url} ')
        with open('fail_pages.txt', 'a', encoding='utf-8') as f:
            f.write(url+'\n')

    # next_page = bs.find('a', string='下一页➡️')
    # if next_page is None:
    #
    #     split_url = re.split(r"(\d{4})\.", url)
    #     pre = split_url[0]
    #     last = split_url[-1]
    #     next_page_num = int(split_url[1]) + 1
    #     next_page_num = "%04d" % next_page_num
    #
    #     # next_page_title = bs.findall('a', string=re.compile(fr"{next_page_num}\. .*")).string
    #     next_page_title = bs.find_all('a', string=re.compile(r"\d{4}\. .*"))
    #     next_page_title = [n.get('href') for n in next_page_title]
    #     for n in next_page_title:
    #         print(n)
    #     next_page = pre + next_page_num + '.' + last
    # else:
    #     next_page = next_page.get('href')
    return data, flag


if __name__ == "__main__":
    url = ""
     headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    html = requests.get(url, headers = headers)
    html.encoding = 'utf-8'
    bs = BeautifulSoup(html.text, "html.parser")
    all_pages = bs.find_all('a', string=re.compile(r"\d{4}\. .*"))
    all_pages = [ap.get('href') for ap in all_pages]

    all_data = []
    for i, p in enumerate(all_pages):
        # if i == 100:
        #     break
        print(f'processing the url {p}')
        data, flag = get_code_info(p)

        if flag:
            all_data.append(data)
            rand = random.randint(1, 5)
            time.sleep(rand)
            if i % 10 == 0:
                print(f'processing the {i}th data......', end='\n')
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)