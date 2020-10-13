import requests
from bs4 import BeautifulSoup
import csv
import telebot
import config
import proxy_moule
import random_user_agent

bot = telebot.TeleBot(config.TOKEN)

URL = 'https://www.avito.ru/'

# FILE = 'users_results/'
message_id_to_del = []


# Функция возвращающая html страницу [params - неоходим для доп параметров страницы к примеру для номера страницы]
def get_html(url, params=None):
    r = requests.get(url, headers=random_user_agent.random_headers(), params=params)
    return r


def get_html_proxy(url, proxy, params=None):
    r = requests.get(url, headers=random_user_agent.random_headers(), params=params, proxies={'http': proxy})
    return r


def get_content(html):
    # Первый параметр сама страница, 2 - опциональный  'html.parser'
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div',
                          class_='description item_table-description')  # soup.find('a', class_='cover anime-tooltip-processed').find_next('span').get_text()
    collection = []
    for item in items:
        metro_distance = item.find('span', class_='item-address-georeferences-item__after')
        if metro_distance:
            metro_distance = metro_distance.get_text()
        else:
            metro_distance = ' дистанция не указана'
        metro = item.find('span', class_='item-address-georeferences-item__content')
        if metro:
            metro = metro.text
        else:
            metro = 'метро не указано'
        collection.append({
            'vacancy': item.find('a', class_='snippet-link').find_next('span').get_text(strip=True).replace('\n ', ''),
            'salary': item.find('div', class_='snippet-price-row').find_next('span').get_text(strip=True).replace(
                '\n ', ''),
            'distance': metro + ', ' + metro_distance.replace('\xa0', ' '),
            'link': 'https://www.avito.ru/' + item.find('a', class_='snippet-link').get('href')
        })
    return collection


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='pagination-item-1WyVp')
    count = 0
    if pagination:
        for item in pagination:
            count += 1
        return int(pagination[count - 2].get_text())
    else:
        return 1


def save_file(items, path):
    with open(path, 'w', newline='',
              encoding='utf-8') as file:  # при конструкции with open файл закрывается автоматически если кто не знал О_о
        writer = csv.writer(file, delimiter=';')  # Разделяю и властвую в екселе ;
        writer.writerow(['Вакансия', 'Зарплата', 'Расстояние от метро',
                         'Ссылка'])  # Данные блин передаю)))
        for item in items:
            writer.writerow([item['vacancy'], item['salary'], item['distance'], item['link']])


def main_parse(message, fname, proxy=None):
    if proxy is None:
        html = get_html(URL)
    else:
        html = get_html_proxy(URL, proxy=proxy)

    collection = []
    pages_count = get_pages_count(html.text)
    for page in range(1, pages_count + 1):
        # if page != 1:
        #     bot.delete_message(message.chat.id, message_id_to_del[-1] - 1)

        if page != 1:
            bot.edit_message_text(f'Сканю страницу {page} из {pages_count}', message.chat.id, message_id_to_del[-1])
        elif page == 1:
            message_id_to_del.append(bot.send_message(message.chat.id, f'Сканю страницу {page} из {pages_count}').message_id) # TODO edit_message_text

        # print(message_id_to_del[-1])
        #bot.send_message(message.chat.id, f'Сканю страницу {page} из {pages_count}')
        #print(message_id_to_del[-1])
        if proxy is None:
            html = get_html(URL, params={'page': page})
        else:
            html = get_html_proxy(URL, proxy=proxy, params={'page': page})

        collection.extend(
            get_content(html.text))  # Ну типа беру весь контент с полученной хтмл и парсю в презентабельный вид

    FILE = f"users_results/{fname}.csv"
    save_file(collection, FILE)
    bot.send_message(message.chat.id, f'Отсканировано {len(collection)} вакансий')


# Основная функция для вызова всех.... Чего всех то? Что она вызывает блять? Умственную отсталость? Нахуя я вообще это пишу....
def parse(message, fname):

    #proxys = proxy_moule.get_connection() # get proxy from list
    bot.send_message(message.chat.id, 'Обновляю список прокси подключений...\n'
                                      'Если я не сделаю это, то у меня внутри все поломается понимаешь? О_О\n'
                                      'Поэтому подожди немножечко...')
    try:
        proxy_moule.proxy_work.upd_proxylist_main() # uodate proxy list function
    except Exception as e:
        print(f'Method({parse.__name__})\n'
              f'Update error\n'
              f'Error:\n{e}\n'
              f'========================')

    for proxy in proxy_moule.proxy_work.get_proxylist_main(): # proxy_moule.get_connection()
        html = get_html_proxy(URL, proxy=proxy)

        # TODO Сюда интегрировать прикол с гифкой

        # print(f'{proxy} СЮДА СМОТРИ ')
        # print(proxy_moule.proxy_work.from_file_proxy_list[0])

        # новая версия ПОСООООООООСИИИИИИИИ)))
        if proxy != proxy_moule.proxy_work.from_file_proxy_list[0]:
            bot.edit_message_text(f'Подключаюсь к {proxy}\nСтатус код: {html.status_code}', message.chat.id, message_id_to_del[-1])
        elif proxy == proxy_moule.proxy_work.from_file_proxy_list[0]:
            message_id_to_del.append(bot.send_message(message.chat.id, f'Подключаюсь к {proxy}\nСтатус код: {html.status_code}').message_id)

        # старая версия сак соме дик О_о
        # bot.send_message(message.chat.id, f'Conecting to {proxy}\n'
        #                                   f'Status code {html.status_code}')

        if html.status_code == 200:
            bot.send_message(message.chat.id,
                             "Оп, я подключился к прокси 😎\n"
                             "Теперь то я быстренько оприходую все вакансии...")
            main_parse(message, fname, proxy=proxy)
            return True
    return False