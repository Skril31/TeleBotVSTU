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
    global master
    master = False
    mbPrepod = False
    for d in dic:
        if user_id == d['id']:
            reg = True
            if(d['subgroup'] == -1):
                mbPrepod = True
            if d['master'] == 1:
                master = True

    if reg and not master and not mbPrepod:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Получить расписание на неделю")
        btn2 = types.KeyboardButton("Получить расписание преподавателя")
        btn3 = types.KeyboardButton("Получить расписание на сегодня")
        btn4 = types.KeyboardButton("Посмотреть объявления преподавателей за последние 7 дней")
        btn5 = types.KeyboardButton("📖 Инструкция")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Я бот расписание ВолгГТУ.".format(
                             message.from_user), reply_markup=markup)
    elif reg and master:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Посмотреть свое расписание")
        btn2 = types.KeyboardButton("Добавить объявление")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Я бот расписание ВолгГТУ.".format(
                             message.from_user), reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Указать группу")
        btn2 = types.KeyboardButton("Я преподаватель")
        markup.add(btn1, btn2)
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

    if(message.text == "Указать группу"):
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
        r = requests.get('http://localhost:8080/lessons/weekDay/' + my_date.strftime("%A") + '/weekType/' + str((week_number%2)) + '/group/' + inf['group'] + '/subgroup/' + str(inf['subgroup'])).text
        v = requests.get('http://localhost:8080/lessons/weekDay/' + my_date.strftime("%A") + '/weekType/' + str((week_number % 2)) + '/group/' + inf['group'] + '/subgroup/' + str(0)).text
        try:
            resStr = my_date.strftime("%A") + '\n\n'
            try:
                res = json.loads(r)
                for sc in res:
                    resStr += 'Начало занятия: ' + sc['start_time'] + '\n'
                    resStr += 'Конец занятия: ' + sc['end_time'] + '\n'
                    resStr += 'Преподаватель: ' + sc['teacher']['fio'] + '\n'
                    resStr += 'Тип занятия: ' + sc['lesson_type']['name'] + '\n'
                    resStr += 'Предмет: ' + sc['subjects']['name'] + '\n'
                    resStr += 'Аудитория: ' + sc['aud']['number'] + ' ' + sc['aud']['corpus'] + '\n\n'
            except Exception:
                print('r pustoi')
            try:
                re = json.loads(v)
                for sc in re:
                    resStr += 'Начало занятия: ' + sc['start_time'] + '\n'
                    resStr += 'Конец занятия: ' + sc['end_time'] + '\n'
                    resStr += 'Преподаватель: ' + sc['teacher']['fio'] + '\n'
                    resStr += 'Тип занятия: ' + sc['lesson_type']['name'] + '\n'
                    resStr += 'Предмет: ' + sc['subjects']['name'] + '\n'
                    resStr += 'Аудитория: ' + sc['aud']['number'] + ' ' + sc['aud']['corpus'] + '\n\n'
            except Exception:
                print('v pustoi')
            #merged_dict = {key: value for (key, value) in (res.items() + re.items())}

            bot.send_message(message.chat.id, text=resStr)
            #start(message)
        except Exception as e:
            bot.send_message(message.chat.id, text="Похоже что в этот день нет занятий")
            print(e)

    elif(message.text == 'Получить расписание преподавателя'):
        bot.send_message(message.chat.id, text="Введи имя преподавателя")
        bot.register_next_step_handler(message, get_teacher)
    elif(message.text == 'Получить расписание на неделю'):
        my_date = date.today()
        # weektype
        gr = requests.get('http://localhost:8080/users/' + str(message.from_user.id)).text
        inf = json.loads(gr)
        calendar.day_name[my_date.weekday()]
        locale.setlocale(locale.LC_ALL, '')
        # Получение текущей даты
        current_date = datetime.datetime.now()
        # Определение номера недели
        week_number = current_date.isocalendar()[1]
        r = requests.get('http://localhost:8080/lessons/weekType/' + str(week_number % 2) + '/group/' + inf['group']).text
        try:
            resStr = "Расписание на эту неделю: \n\n"
            res = json.loads(r)
            for sc in res:
                resStr += 'День недели: ' + sc['weekDay'] + '\n'
                resStr += 'Начало занятия: ' + sc['start_time'] + '\n'
                resStr += 'Конец занятия: ' + sc['end_time'] + '\n'
                resStr += 'Преподаватель: ' + sc['teacher']['fio'] + '\n'
                resStr += 'Тип занятия: ' + sc['lesson_type']['name'] + '\n'
                resStr += 'Предмет: ' + sc['subjects']['name'] + '\n'
                resStr += 'Аудитория: ' + sc['aud']['number'] + ' ' + sc['aud']['corpus'] + '\n\n'
        except Exception:
            print()
        bot.send_message(message.chat.id, text=resStr)
        #start(message)
    elif message.text == 'Посмотреть объявления преподавателей за последние 7 дней':
        gr = requests.get('http://localhost:8080/users/' + str(message.from_user.id)).text
        inf = json.loads(gr)
        r = requests.get('http://localhost:8080/ad/' + inf['group'] + '/list')
        resStr = 'Объявления преподавателей за последние 7 дней: \n\n'
        try:
            resu = json.loads(r.content)

            for sc in resu:
                if datetime.datetime.now() - datetime.datetime.fromisoformat(sc['localDateTime'])  <= datetime.timedelta(days=7):
                    resStr += 'Преподаватель: ' + sc['teacher_name'] + '\n'
                    resStr += 'Объявление: ' + sc['text'] + '\n\n'
        except Exception as e:
            print(e)
        bot.send_message(message.chat.id, text=resStr)
    elif message.text == 'Я преподаватель':
        bot.send_message(message.chat.id, text="Введите свои фамилию и инициалы (Например Иванов А.А.)")
        bot.register_next_step_handler(message, post_teacher_name)

    elif message.text == 'Добавить объявление':
        bot.send_message(message.chat.id, text="Введите название группы для которой хотите сделать объявление:")
        bot.register_next_step_handler(message, group_for_ad)

    elif message.text == 'Посмотреть свое расписание':
        r = requests.get("http://localhost:8080/users/" + str(message.chat.id))
        res = json.loads(r.content)
        v = requests.get('http://localhost:8080/teachers/' + res['group'] + '/lessons').text
        resStr = ''
        try:
            res = json.loads(v)
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
        except Exception:
            bot.send_message(message.chat.id, text="Такой преподаватель не найден")

def group_for_ad(message):
    global group
    group = message.text
    bot.send_message(message.chat.id, text="Введите объявление:")
    bot.register_next_step_handler(message, post_ad)
def post_ad(message):
    ad = message.text
    global group
    r = requests.get("http://localhost:8080/users/" + str(message.chat.id))
    res = json.loads(r.content)
    loadAd = {
        "teacher_name": res['group'],
        "text": ad,
        "groups": group
    }
    r = requests.post('http://localhost:8080/ad', json=loadAd)
    bot.send_message(message.chat.id, text="Объявление добавлено")
    usersresponse = requests.get('http://localhost:8080/users/' + group + '/list').text
    users = json.loads(usersresponse)
    rStr = "Объявление от преподавателя:\n\nПреподаватель: " + res['group'] + "\n\nОбъявление: " + ad
    for user in users:
        bot.send_message(chat_id=user['id'], text=rStr)
    start(message)
def post_teacher_name(message):
    teacher = message.text
    loaduser = {'id': message.from_user.id,
                'group': teacher,
                "subgroup": -1}
    r = requests.post('http://localhost:8080/users', json=loaduser)
    bot.send_message(message.chat.id, text='Вы зарегистрировались, теперь подождите пока администратор одобрит вашу заявку. После одобрения заявки пропишите /start и ваш интерфейс поменяется.')
    start(message)

# def get_teacher_for_teacher():
#     r = requests.get("http://localhost:8080/users/" + str(user_chat_id))
#     res = json.loads(r)
#     v = requests.get('http://localhost:8080/teachers/' + res['group'] + '/lessons').text
#     resStr = ''
#     try:
#         res = json.loads(v)
#         for sc in res:
#             resStr += 'День недели: ' + sc['weekDay'] + '\n'
#             resStr += 'Номер недели: ' + str(sc['weekType']) + '\n'
#             resStr += 'Начало занятия: ' + sc['start_time'] + '\n'
#             resStr += 'Конец занятия: ' + sc['end_time'] + '\n'
#             resStr += 'Группа: ' + sc['groups']['groupName'] + '\n'
#             resStr += 'Подгруппа: ' + str(sc['groups']['subgroup']) + '\n'
#             resStr += 'Тип занятия: ' + sc['lesson_type']['name'] + '\n'
#             resStr += 'Предмет: ' + sc['subjects']['name'] + '\n'
#             resStr += 'Аудитория: ' + sc['aud']['number'] + ' ' + sc['aud']['corpus'] + '\n\n'
#         bot.send_message(user_chat_id, text=resStr)
#     except Exception:
#         bot.send_message(user_chat_id, text="Такой преподаватель не найден")
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
    dic = [{'group': '', 'sub': 0, 'dt': '00:00:00'}]
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
                flag =True
                if len(dic) != 0:
                    for d in dic:

                        if d['group'] == ls['groups']['groupName'] and d['sub'] == ls['groups']['subgroup']:
                            flag = False

                        if (dt - datetime.datetime.strptime(d['dt'], "%H:%M:%S")) >= datetime.timedelta(minutes=50):
                            dic.remove(d)
                if (abs(dt - datetime.datetime.strptime(ls['start_time'], "%H:%M:%S")) <= datetime.timedelta(minutes=30)) and (ls['weekDay'] == my_date.strftime("%A")) and (ls['weekType'] == ((week_number % 2))) and flag:
                    group = ls['groups']['groupName']
                    sub = ls['groups']['subgroup']
                    #добавлять даные в словарь а затем проверять прошел ли час с момента добавления записи если прошел то удалять данные
                    dic1 = {'group': group, 'sub': sub, 'dt': datetime.datetime.now().strftime("%H:%M:%S")}
                    dic.append(dic1)
                    #for di in dic:
                        #if di['dt'] >= datetime.timedelta(minutes=40):
                    resStr = 'Скоро начнется занятие: \n'
                    resStr += 'Начало занятия: ' + ls['start_time'] + '\n'
                    resStr += 'Конец занятия: ' + ls['end_time'] + '\n'
                    resStr += 'Преподаватель: ' + ls['teacher']['fio'] + '\n'
                    resStr += 'Тип занятия: ' + ls['lesson_type']['name'] + '\n'
                    resStr += 'Предмет: ' + ls['subjects']['name'] + '\n'
                    resStr += 'Аудитория: ' + ls['aud']['number'] + ' ' + ls['aud']['corpus'] + '\n\n'
                    if sub == 0:
                        users1 = requests.get('http://localhost:8080/users/group/' + group + '/subgroup/' + str(1)).text
                        users2 = requests.get('http://localhost:8080/users/group/' + group + '/subgroup/' + str(2)).text
                        try:
                            usersInfo1 = json.loads(users1)
                            for user in usersInfo1:
                                bot.send_message(chat_id=user['id'], text=resStr)
                        except:
                            print("net 1 pg")
                        try:
                            usersInfo2 = json.loads(users2)
                            for user in usersInfo2:
                                bot.send_message(chat_id=user['id'], text=resStr)
                        except:
                            print("net 2 pg")

                    else:
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

    except Exception as e:
        bot.send_message(user_chat_id,text="Ошибка в системе оповещений")
        print(e)
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

