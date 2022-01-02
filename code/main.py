import requests
import json
import re
import pandas as pd
from lxml import etree


def get_html(url,way='get'):
    '''
    请求获取 html 网页
    :param package_download_url:
    :return:
    '''
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }
    count = 1
    while True:
        if way == 'get':
            response = requests.get(url,headers=headers)
            response.encoding = 'utf8'
            return response.text
        else:
            try: # 代表请求失败
                response = requests.post(url,headers=headers)
            except:
                count += 1
                if count == 3:
                    return
                continue
            try: # 代表查不到包信息
                return response.json()
            except:
                return


def get_package(html):
    '''
    提取所有包名
    :param package_download_html:
    :return:
    '''
    html = etree.HTML(html.encode('utf-8'))
    label = html.xpath('//ul[@class="pylibs"]/li/ul/li')
    package = []
    for l in label:
        p = l.xpath('string(.)')
        p = p.split('‑')[0]
        package.append(p)
    return set(package)


def get_describe_download(p):
    '''
    提取
    :param p:
    :return:
    '''
    # 包详情
    describe_url = 'https://www.pyprapi.top/pypi_api/{}'.format(p)
    describe_json = get_html(describe_url,way='post')
    if describe_json == None:
        print('{} 请求失败！！！'.format(p))
        return '',''
    describe = describe_json['message']['info']['description']
    # 包近 30 天下载量
    download_url = 'https://www.pyprapi.top/pypi_project_downloads/{}'.format(p)
    download_json = get_html(download_url,way='post')
    download = download_json['message']
    download = re.findall('近三十天总的下载总量为: (.*?) 次',download)[0]

    return describe,download


def main():
    '''
    主逻辑
    :return:
    '''
    # 获取包名
    package_download_url = 'https://www.lfd.uci.edu/~gohlke/pythonlibs/'
    package_download_html = get_html(package_download_url,'get')
    package = get_package(package_download_html)

    # 获取库的简介描述，近 30 天下载量
    df = []
    for i,p in enumerate(package):
        describe,download = get_describe_download(p)
        df.append([p,download,describe])
        print('{} 近30天有 {} 次下载量 {}/{}'.format(p,download,str(i+1),str(len(package))))

    # 保存数据
    try:
        data = pd.DataFrame(df,columns=['package','download','describe'])
        data.to_csv('../data/package.csv',index=False,encoding='utf8')
    except:
        print(df)


if __name__ == '__main__':
    main()










