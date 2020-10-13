import requests
from bs4 import BeautifulSoup
import random_user_agent
import my_proxy_list
import multiprocessing

# НУ ОН ПОКА ЧТО НИ ГДЕ НЕ ЮЗАЕТСЯ ЕСЛИ ЧТО, ЕГО ВООБЩЕ МОЖНО УДАЛИТЬ В ПРИНЦИПЕ, НО Я РЕШИЛ ОСТАВИТЬ))))
# THE MODULE IS NOT USED ANYWHERE YET, IT CAN BE REMOVED IF ANYTHING

domain_start = 'https://hidemy.name/ru/proxy-list'  # table_block
table_rows = 64
nums_cpu = multiprocessing.cpu_count()


def get_html(url, params=None):
    r = requests.get(url, headers=random_user_agent.random_headers(), params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='pagination')
    pagination = table.find_all('a')
    count = 0
    if pagination:
        for item in pagination:
            count += 1
        print()
        return int(pagination[count - 2].get_text())
    else:
        return 1


def get_proxylist(html): # scan all
    proxy_collection = []

    pages_count = get_pages_count(html)  # TODO  64
    count_distance = 0
    for page in range(1, pages_count + 1):
        # html = get_html(domain_start, params={'page': page}) #
        html = get_html(domain_start, params={'start': count_distance})
        count_distance += table_rows  # TODO
        soup = BeautifulSoup(html.text, 'html.parser')

        table = soup.find('tbody')
        collection = table.find_all('tr')
        for item in collection:
            res = item.find('td').text
            proxy_collection.append(res)
    return proxy_collection


def append_proxy():
    my_proxy_list.proxy_list = get_proxylist(get_html(domain_start).text)

# UPD
def get_proxylist_parallel(count_distance):  # scan for core
    proxy_collection = []

    html = get_html(domain_start, params={'start': count_distance})
    soup = BeautifulSoup(html.text, 'html.parser')
    print(soup) # Могут забанить TODO
    table = soup.find('tbody')
    collection = table.find_all('tr')
    for item in collection:
        res = item.find('td').text
        proxy_collection.append(res)

    my_proxy_list.proxy_list.append(proxy_collection)



def parallel_get_list(html):
    # pages_count = get_pages_count(html)
    # pages_count = 28
    # print(pages_count)
    #
    #
    # page_for_core =  pages_count // nums_cpu # page for core  get_pages_count(html)
    # print(page_for_core)
    #
    # pages = [] # list of list
    #
    # pg_start = 1
    # pg_end = page_for_core
    # for i in range(pg_end, nums_cpu): # 1 to 25 pages_count
    #     page = list()
    #     page.append(pg_start)  # page_start
    #     page.append(pg_end)  # page_end
    #
    #     pg_start = pg_end + 1
    #     pg_end = page_for_core * i
    #     pages.append(page)
    #
    #
    # for pgs in pages:
    #     for pg in pgs:
    #         print(f'{pg},')
    #     print('_____')


    for i in my_proxy_list.proxy_list:
        print(i)

    # pages_count = get_pages_count(html)
    # print(pages_count)

    count_distance = 0
    if __name__ == '__main__':
        for i in range(1, 8): # pages_count
            t = multiprocessing.Process(target=get_proxylist_parallel, args=(count_distance,))
            t.start()
            count_distance += 64

    for i in my_proxy_list.proxy_list:
        print(i)


    # if __name__ == '__main__':
    #     for i in range(1, 8): # pages_count
    #         t = multiprocessing.Process(target=work, args=(i,))
    #         t.start()



# parallel_get_list(get_html(domain_start).text) # TODO