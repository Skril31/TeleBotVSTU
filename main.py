import time
from threading import Thread

import telebot
from telebot import types
import requests
import json
import datetime
from datetime import date

import locale
import calendar
import random


bot = telebot.TeleBot('6189016042:AAFAx4cBWX8sIkUXgOygs_BEfYzkbHTAdxc')
#group = 'BDN'
#subgroup = 1
user_chat_id = 'USER_CHAT_ID'
@bot.message_handler(commands=["start"])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    register = requests.get('http://localhost:8080/users').text
    dic = json.loads(register)
    user_id = message.from_user.id
    reg = False
    for d in dic:
        if user_id == d['id']:
            reg = True
    if reg:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Получить расписание на неделю")
        btn2 = types.KeyboardButton("Получить расписание преподавателя")
        btn3 = types.KeyboardButton("Получить расписание на сегодня")
        #btn4 = types.KeyboardButton("Посмотреть объявления преподавателей на сегодня")
        btn5 = types.KeyboardButton("📖 Инструкция")
        markup.add(btn1, btn2, btn3, btn5)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Я бот расписание ВолгГТУ.".format(
                             message.from_user), reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Указать группу")
        markup.add(btn1)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Я бот расписание ВолгГТУ. Укажи пожалуйста свою группу.".format(
                             message.from_user), reply_markup=markup)
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,text="Помогаю")

def send_notification():
    bot.send_message(chat_id=user_chat_id, text='Ваше уведомление')


@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "🎲 Случайный фильм/сериал"):
        bot.send_message(message.chat.id,text="Введите рейтинг больше которого хотите увидеть результат(от 0 до 10)")
        #bot.register_next_step_handler(message,rand)

    elif(message.text == "Указать группу"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("ИВТ-363")
        btn2 = types.KeyboardButton("ИВТ-365")
        btn3 = types.KeyboardButton("ИВТ-360")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text="Какая у тебя группа?", reply_markup=markup)
        bot.register_next_step_handler(message, get_group)

    elif(message.text == "Получить расписание на сегодня"):
        my_date = date.today()
        #weektype
        gr = requests.get('http://localhost:8080/users/' + str(message.from_user.id)).text
        inf = json.loads(gr)
        calendar.day_name[my_date.weekday()]
        locale.setlocale(locale.LC_ALL, '')
        # Получение текущей даты
        current_date = datetime.datetime.now()
        # Определение номера недели
        week_number = current_date.isocalendar()[1]
        r = requests.get('http://localhost:8080/lessons/weekDay/' + my_date.strftime("%A") + '/weekType/' + str((week_number%2)+1) + '/group/' + inf['group'] + '/subgroup/' + str(inf['subgroup'])).text
        try:
            res = json.loads(r)
            resStr = my_date.strftime("%A") + '\n\n'
            for sc in res:
                resStr += 'Начало занятия: ' + sc['start_time'] + '\n'
                resStr += 'Конец занятия: ' + sc['end_time'] + '\n'
                resStr += 'Преподаватель: ' + sc['teacher']['fio'] + '\n'
                resStr += 'Тип занятия: ' + sc['lesson_type']['name'] + '\n'
                resStr += 'Предмет: ' + sc['subjects']['name'] + '\n'
                resStr += 'Аудитория: ' + sc['aud']['number'] + ' ' + sc['aud']['corpus'] + '\n\n'
            bot.send_message(message.chat.id, text=resStr)
            start(message)
        except Exception:
            bot.send_message(message.chat.id, text="Похоже что в этот день нет занятий")

    elif(message.text == 'Получить расписание преподавателя'):
        bot.send_message(message.chat.id, text="Введи имя преподавателя")
        bot.register_next_step_handler(message, get_teacher)


def get_teacher(message):
    global teacher
    teacher = message.text
    r = requests.get('http://localhost:8080/teachers/' + teacher + '/lessons').text
    resStr = ''
    try:
        res = json.loads(r)
        for sc in res:
            resStr += 'День недели: ' + sc['weekDay'] + '\n'
            resStr += 'Номер недели: ' + str(sc['weekType']) + '\n'
            resStr += 'Начало занятия: ' + sc['start_time'] + '\n'
            resStr += 'Конец занятия: ' + sc['end_time'] + '\n'
            resStr += 'Группа: ' + sc['groups']['groupName'] + '\n'
            resStr += 'Подгруппа: ' + str(sc['groups']['subgroup']) + '\n'
            resStr += 'Тип занятия: ' + sc['lesson_type']['name'] + '\n'
            resStr += 'Предмет: ' + sc['subjects']['name'] + '\n'
            resStr += 'Аудитория: ' + sc['aud']['number'] + ' ' + sc['aud']['corpus'] + '\n\n'
        bot.send_message(message.chat.id, text=resStr)
    except Exception :
        bot.send_message(message.chat.id, text="Такой преподаватель не найден")



def get_group(message):
    global group
    group = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("1")
    btn2 = types.KeyboardButton("2")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, 'Какая у тебя подгруппа?', reply_markup=markup)
    bot.register_next_step_handler(message, get_subgroup)

def get_subgroup(message):
    global subgroup
    subgroup = message.text

    loaduser = {'id': message.from_user.id,
        'group': group,
        "subgroup": int(subgroup)}
    r = requests.post('http://localhost:8080/users', json=loaduser)
    start(message)

def notification():
    #users = requests.get('http://localhost:8080/users').text
    #usersInfo = json.loads(users)
    lessons = requests.get('http://localhost:8080/lessons').text

    try:
        lessonsInfo = json.loads(lessons)
        while True:
            my_date = date.today()
            calendar.day_name[my_date.weekday()]
            locale.setlocale(locale.LC_ALL, '')
            current_date = datetime.datetime.now()
            week_number = current_date.isocalendar()[1]
            time.sleep(1)
            #dic = {}
            for ls in lessonsInfo:
                dt = datetime.datetime.now()
                dtForm = dt.strftime("%H:%M:%S")
                dt = datetime.datetime.strptime(dtForm, "%H:%M:%S")
                if (abs(dt - datetime.datetime.strptime(ls['start_time'], "%H:%M:%S")) <= datetime.timedelta(minutes=30)) and (ls['weekDay'] == my_date.strftime("%A")) and (ls['weekType'] == ((week_number % 2)+1)):
                    group = ls['groups']['groupName']
                    sub = ls['groups']['subgroup']
                    #добавлять даные в словарь а затем проверять прошел ли час с момента добавления записи если прошел то удалять данные
                    dic = [{'group': group, 'sub': sub, 'dt': datetime.datetime.now()}]
                    users = requests.get('http://localhost:8080/users/group/' + group + '/subgroup/' + str(sub)).text
                    try:
                        usersInfo = json.loads(users)


                        resStr = 'Скоро начнется занятие: \n'
                        resStr += 'Начало занятия: ' + ls['start_time'] + '\n'
                        resStr += 'Конец занятия: ' + ls['end_time'] + '\n'
                        resStr += 'Преподаватель: ' + ls['teacher']['fio'] + '\n'
                        resStr += 'Тип занятия: ' + ls['lesson_type']['name'] + '\n'
                        resStr += 'Предмет: ' + ls['subjects']['name'] + '\n'
                        resStr += 'Аудитория: ' + ls['aud']['number'] + ' ' + ls['aud']['corpus'] + '\n\n'

                        for user in usersInfo:

                            bot.send_message(chat_id=user['id'], text=resStr)
                    except Exception:
                        print("")

    except Exception:
        bot.send_message(user_chat_id,text="Ошибка в системе оповещений")
    #my_date = date.today()
    #gr = requests.get('http://localhost:8080/users/' + str(user_chat_id)).text
    # inf = json.loads(gr)
    # calendar.day_name[my_date.weekday()]
    # locale.setlocale(locale.LC_ALL, '')
    #
    # current_date = datetime.datetime.now()
    #
    # week_number = current_date.isocalendar()[1]
    # r = requests.get('http://localhost:8080/lessons/weekDay/' + my_date.strftime("%A") + '/weekType/' + str((week_number%2)+1) + '/group/' + inf['group'] + '/subgroup/' + str(inf['subgroup'])).text


# @bot.callback_query_handler(func=lambda call:True)
# def callback(call):
#     if call.message:
#         if call.data == '363':
#             group = "ИВТ-363"





   # elif(message.text == "🎬 Подборка"):
tread1 = Thread(target=notification, args=())
tread1.start()
bot.polling(none_stop=True, interval=0)

