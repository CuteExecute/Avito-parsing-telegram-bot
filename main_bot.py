import telebot
import config
import random
import go_parse

bot = telebot.TeleBot(config.TOKEN)
user_id = None


def rnd_hello():
    hello_words = {'1': 'самый лучший', '2': 'восхитеительный', '3': 'великолепный', '4': 'замечательный',
                   '5': 'красивый'}
    num = random.choice(range(1, 6))
    return hello_words[f"{num}"]


def rnd_post():
    path = [['Компутирный кит :о)', 'recourse/compCat.gif.mp4'], ['Кирпичь В-)', 'recourse/Kirpich.gif.mp4']]
    num = random.choice(range(0, 2))
    return path[num]


def check_address(adr=None):
    if adr.find('?') != -1:
        adr = adr.split('?')[0]
    if adr.find('avito.ru') != -1:
        if (adr.find('/vakansii') != -1) or (adr.find('/rabota') != -1):
            return True
        else:
            return False
    else:
        return False
    pass


@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(message.chat.id,
                     f"Привет {rnd_hello()} пользователь компьютерных технологий {message.from_user.first_name}!\n"
                     f"Я бот который отпарсит как следует список вакансий с avito.ru\n"
                     f"Я ожидаю ссылку в формате: <i>https://www.avito.ru/</i>\n",
                     parse_mode='html')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, f"Привет-помоч?\n"
                                      f"/help - <i>обучательный интерфейс</i>\n"
                                      f"/start - <i>ЗАПУСТИ МЕНЯ</i>\n"
                                      f"/last - <i>Гив ми ласт результ</i>\n", parse_mode='html')


@bot.message_handler(commands=['last'])
def send_file(message):
    f = open(f'users_results/{message.chat.id}.csv', 'rb')
    bot.send_document(message.chat.id, f, timeout=100)


@bot.message_handler(content_types=['text'])
def start_parse(message):
    if check_address(message.text):
        user_id = message.chat.id  # юзер id как имя файла
        print(user_id)  # TODO Ну пусть будет в принципе, не сильно мешает :)

        try:  # TODO ловим ошибки всякие)))
            go_parse.URL = message.text
            success = go_parse.parse(message, user_id)

            if success:
                send_file(message)
                stick = open('recourse/work.webp', 'rb')
                bot.send_sticker(message.chat.id, stick)
            else:
                bot.send_message(message.chat.id, "Соеденение не установлено\n"
                                                  "Ни один из прокси серверов не подошел :с")

        except Exception as e:
            print(f'Method({start_parse.__name__})\n'
                  f'Error:\n{e}\n'
                  f'========================')
            bot.send_message(message.chat.id, f'Возникла проблемка...\n'
                                              f'Error:\n{e}\n')
    else:
        bot.send_message(message.chat.id,
                         f"[<i>калибрую настройки...</i>]\n"
                         f"А тебе, {message.from_user.first_name}, лучше бы откалибровать свою голову и отправить мне нормальную ссылку...\n",
                         parse_mode='html')


@bot.message_handler(content_types=['audio', 'video', 'document', 'location', 'contact', 'sticker'])
def show_sticker_answer(message):
    post = rnd_post()
    bot.send_message(message.chat.id, post[0])
    gif = open(post[1], 'rb')
    bot.send_animation(message.chat.id, gif)


# Run
if __name__ == "__main__":
    bot.polling(none_stop=True)
