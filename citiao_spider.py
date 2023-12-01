import pandas as pd
from config import *

from bs4 import BeautifulSoup
import requests

from tqdm import tqdm
import math

def get_summary(url: str):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        return '请求失败'
    html_cont = response.text
    if '抱歉，百度百科尚未收录词条' in html_cont or 'baike.baidu.com/error.html' in html_cont:
        return '百度百科尚未收录词条'
    soup = BeautifulSoup(html_cont, 'lxml')

    # title = soup.title.string
    try:
        description = soup.find('meta', attrs={'name': 'description'})['content']
    except:
        return '页面不存在'
    return description


def get_describe(dataframe):
    not_found = []
    for index, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0]):
        name = row['名称']
        if (isinstance(name, float) and math.isnan(name)) or  (isinstance(name, str) and name.strip()) == '' or name is None:
            dataframe.loc[index, '描述'] = None
        else:
            url = 'https://baike.baidu.com/item/' + name
            description = get_summary(url)
            dataframe.loc[index, '描述'] = description   
    return dataframe


if __name__ == "__main__":
    file_path = './各省特色整理.xlsx'
    save_path = './各省特色整理_描述.xlsx'
    with pd.ExcelFile(file_path) as xls:
        sheet_names = xls.sheet_names

    with pd.ExcelWriter(save_path) as writer:
        for sheet_name in sheet_names:
            print(sheet_name, '开始爬取')
            dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
            dataframe = get_describe(dataframe)
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            print(sheet_name, '爬取完成')