import requests
from bs4 import BeautifulSoup
import re
import random_user_agent
import multiprocessing
from itertools import groupby


class proxy_work:
    # Поле класса, которое будет содержать полный список прокси
    proxy_list = []  # только что отсканированные прокси
    from_file_proxy_list = []  # прокси из файла
    nums_cpu = multiprocessing.cpu_count()  # вдруг пригодится кол-во ядер сипию
    file = 'my_proxy_list.txt'  # файлик для записи

    # Получение страницы
    @staticmethod
    def get_html(url, params=None):
        r = requests.get(url, headers=random_user_agent.random_headers(), params=params)
        return r

    @staticmethod
    def get_html_proxy(url, proxy, params=None):
        r = requests.get(url, headers=random_user_agent.random_headers(), params=params, proxies={'http': proxy})
        return r

    @staticmethod
    def save_result_for_file(list):
        with open(proxy_work.file, 'w', newline='', encoding='utf-8') as file:
            for string in list:
                if string == list[0]:
                    file.write(f'{string}')
                else:
                    file.write(f'\n{string}')

    @staticmethod
    def proxy_check():  # TODO нашел применение
        for proxy in proxy_work.get_proxylist_main():  # proxy_work.from_file_proxy_list
            print(f'TARGET - {proxy_work.from_file_proxy_list}') # TODO
            html = proxy_work.get_html_proxy('https://hidemy.name/ru/proxy-list',
                                             proxy=proxy)  # https://hidemy.name/ru/proxy-list   https://www.google.ru/
            print(f'proxy = {proxy}({html.status_code})')
            if html.status_code == 200:
                return proxy
        print('Proxy check is failed')
        return None

    @staticmethod  # main method
    def upd_proxylist_main():
        proxylist_1 = proxy_work.proxy_n1.get_proxy_list(proxy_work.get_html(proxy_work.proxy_n1.domain_start).text)
        proxy_work.proxy_list.append(proxylist_1)

        good_proxy = proxy_work.proxy_check()
        if good_proxy is None:
            proxylist_2 = proxy_work.proxy_n2.get_proxylist(proxy_work.get_html(proxy_work.proxy_n2.domain_start).text)
        else:
            proxylist_2 = proxy_work.proxy_n2.get_proxylist(proxy_work.get_html(proxy_work.proxy_n2.domain_start).text, good_proxy)  # use proxy
        proxy_work.proxy_list.append(proxylist_2)

        proxylist_1 += proxylist_2

        new_list = [el for el, _ in groupby(proxylist_1)] # удалить одинаковые элементы

        proxy_work.save_result_for_file(new_list) # proxylist_1

        # читаю новые прокси из файла
        proxy_work.get_proxies()
        return proxy_work.from_file_proxy_list

    @staticmethod
    def get_proxylist_main():
        proxy_work.get_proxies()
        return proxy_work.from_file_proxy_list

    @staticmethod
    def get_proxies():
        with open(proxy_work.file, "r", encoding='utf-8') as file:
            proxy_work.from_file_proxy_list = file.readlines()

    class proxy_n1:  # Тут получаю всего одну страничку с проксями
        domain_start = 'https://www.ip-adress.com/proxy-list'

        # Парсинг прокси
        @staticmethod
        def get_proxy_list(html):
            try:
                proxy_collection = []
                soup = BeautifulSoup(html, 'html.parser')

                table = soup.find('table', class_='htable proxylist')

                my_item = table.find('a')
                while not re.match("[A-Za-z]", my_item.text):
                    proxy_collection.extend(my_item)
                    my_item = my_item.find_next('a')

                return proxy_collection
            except Exception as e:
                print(f'Класс({proxy_work.proxy_n1.__name__})\n'
                      f'Method({proxy_work.proxy_n1.get_proxy_list.__name__})\n'
                      f'Error:\n{e}\n'
                      f'========================')

    class proxy_n2:  # Большая такая прокси бейз на 1.5к в среднем проксей
        domain_start = 'https://hidemy.name/ru/proxy-list'  # +- 1024 прокси table_block
        table_rows = 64  # кол во табличных строк

        @staticmethod  # получаем кол-во страниц пагинации
        def get_pages_count(html):
            try:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('div', class_='pagination')
                pagination = table.find_all('a')
                count = 0
                if pagination:
                    for item in pagination:
                        count += 1
                    return int(pagination[count - 2].get_text())
                else:
                    return 1
            except Exception as e:
                print(f'Класс({proxy_work.proxy_n2.__name__})\n'
                      f'Method({proxy_work.proxy_n2.get_pages_count.__name__})\n'
                      f'Error:\n{e}\n'
                      f'========================')


        @staticmethod
        def get_proxylist(html, proxy=None):  # scan all
            try:
                proxy_collection = []

                pages_count = proxy_work.proxy_n2.get_pages_count(html)
                count_distance = 0
                for page in range(1, pages_count + 1):

                    # html = get_html(domain_start, params={'page': page}) #
                    # html = proxy_work.get_html(proxy_work.proxy_n2.domain_start, params={'start': count_distance})
                    if proxy is None:
                        html = proxy_work.get_html(proxy_work.proxy_n2.domain_start, params={'start': count_distance})
                    else:
                        html = proxy_work.get_html_proxy(proxy_work.proxy_n2.domain_start, params={'start': count_distance}, proxy=proxy)

                    count_distance += proxy_work.proxy_n2.table_rows  # TODO
                    soup = BeautifulSoup(html.text, 'html.parser')

                    table = soup.find('tbody')
                    collection = table.find_all('tr')
                    for item in collection:
                        res = item.find('td').text
                        proxy_collection.append(res)
                return proxy_collection
            except Exception as e:
                print(f'Класс({proxy_work.proxy_n2.__name__})\n'
                      f'Method({proxy_work.proxy_n2.get_proxylist.__name__})\n'
                      f'Error:\n{e}\n'
                      f'========================')
