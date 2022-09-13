# -*- coding: utf-8 -*-
import os
from typing import Optional

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from .june import DAO
from .module import Module


main: Optional['Main'] = None


class InformatorModule(Module):
    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "Модуль информирования"

    def module_will_load(self):
        global main
        main = Main()

    def module_will_unload(self):
        pass

    def module_infinite_run(self):
        main.events()


class Main:
    def __init__(self):
        token: str | None = os.environ.get('TOKEN')

        if token is None:
            raise Exception("TOKEN is not in environment!")
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk_api = self.vk_session.get_api()

    def send_msg(self, send_id, msg):
        self.vk_api.messages.send(peer_id=send_id, message=msg, random_id=get_random_id())

    # Функция поиска айди студента по id в вк
    def find_students(self, dao, id):
        s = dao.get_students_list()
        i = 0
        res = -1
        while res < 0 and i < len(s):
            if s[i][4] != '':
                if s[i][4] == id:
                    res = s[i][0]
            i += 1
        if i > len(s):
            return '&#10060;Данный пользователь не найден. Пожалуйста проверьте введенные данные.'
        else:
            return res

    # Вывод списка студентов из БД
    def list_to_str(self, dao):
        s = dao.get_students_list()
        final = ''
        s = list(s)
        for i in range(0, len(s)):
            j = str(i + 1)
            s[i] = list(s[i])
            for k in range(0, len(s[i])):
                if s[i][k] is None:
                    s[i][k] = ''
            final += '\n\n' + j + ".  " + s[i][1] + " " + s[i][2] + '\nGroup: ' + s[i][3] + '\nID-VK: ' + s[i][
                4] + ', ID-Telegram: ' + s[i][5]
        return final

    def events(self):
        dao = DAO()
        start = False
        temp = 0
        IDT = ' '
        # Переменная хранения ФИ
        FIO = [' ', ' ']
        # Переменная хранения номера группы
        Group = ' '
        # Переменная хранения сообщения-рассылки
        buff = ''

        while True:
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if not event.to_me:
                        continue
                    message = event.message
                    id = event.peer_id
                    text = event.message
                    # Бот ТиВПО
                    # Информация
                    if text.lower() == '/exit':
                        main.send_msg(id,
                                      "&#10071;Вы принудительно завершили блок. Список команд можно узнать с помощью /help")
                        temp = 0
                    elif text.lower() == '/help':
                        main.send_msg(id, "СПИСОК КОМАНД"
                                          "\n\nГлавные команды:"
                                          "\n&#128400;  /start — начало работы с ботом (может использоваться только 1 раз);"
                                          "\n&#128214;  /help — список доступных команд;"
                                          "\n&#128100;  /me — изменить данные о себе;"
                                          "\n\nРабота со студентами:"
                                          "\n&#10133;  /new — добавить нового студента в список;"
                                          "\n&#10060;  /del или /delete — удалить запись о студенте;"
                                          "\n&#128101;  /list или /ls — список студентов;"
                                          "\n\n&#9993;  /msg — отправить сообщение-рассылку;"
                                          "\n&#128682;  /exit — принудительно выйти из блока команды.")
                        temp = 0
                    elif text.lower() == '/start':
                        temp = 1
                        if start is False:
                            start = True
                            main.send_msg(id,
                                          "Приветствую&#128400;, я – чат-бот для рассылки полезной информации.\n\nДля начала работы, давай познакомимся!"
                                          "\nНапиши свою имя, а затем фамилию через пробел, для того чтобы я смог внести тебя в базу данных&#9997;")
                        else:
                            main.send_msg(id,
                                          "К сожалению я не могу выполнить данную команду дважды.&#128532;\n\nВведите /help, чтобы познакомиться со списком команд.")
                    elif (temp == 1):
                        FIO = text.split(' ')
                        main.send_msg(id, "Твое имя - " + FIO[0] + '.\nФамилия - ' + FIO[1] + '.\n\nВерно?')
                        temp = 2
                    elif (temp == 2):
                        if text.lower().split(' ')[0] == 'нет':
                            main.send_msg(id,
                                          "Ничего страшного! Давайте попробуем снова. Напишите свое имя, а затем фамилию через пробел")
                            temp = 1
                        elif text.lower() == 'да':
                            main.send_msg(id, "Теперь напишите номер своей группы в формате XXXX-XX-XX")
                            temp = 3
                        else:
                            main.send_msg(id, 'Я вас не понимаю. Повторите ваш ответ (да/нет).')
                    elif (temp == 3):
                        Group = text.upper()
                        dao.add_new_student(FIO[0], FIO[1], Group, id, '')
                        main.send_msg(id,
                                      "Ваши данные сохранены!\nВ любой момент их можно поменять, для этого напишите команду /me")
                        temp = 0
                    elif text.lower() == '/me':
                        main.send_msg(id, "Напишите номер поля, который хотите изменить:\n1. Имя: " + FIO[
                            0] + '.\n2. Фамилия: ' + FIO[1] + '.\n3. Группа: ' + Group + '.\n4. ID Telegram: ' + IDT)
                        temp = 4
                    elif temp == 4:
                        if text != '4':
                            print('b')
                        if text == '1':
                            main.send_msg(id, "Введите новое значение имени:")
                            temp = 5
                        elif text == '2':
                            main.send_msg(id, "Введите новое значение фамилии:")
                            temp = 6
                        elif text == '3':
                            main.send_msg(id, "Введите новое значение группы:")
                            temp = 7
                        elif text == '4':
                            main.send_msg(id, "Введите новое значение ID Telegram:")
                            temp = 8
                        else:
                            main.send_msg(id, "Я вас не понимаю&#128532;, повторите ваш запрос, пожалуйста")
                    elif temp == 5:
                        dao.delete_student_by_id(id)
                        FIO[0] = text
                        dao.add_new_student(FIO[0], FIO[1], Group, id, IDT)
                        temp = 0
                    elif temp == 6:
                        dao.delete_student_by_id(id)
                        FIO[1] = text
                        dao.add_new_student(FIO[0], FIO[1], Group, id, IDT)
                        temp = 0
                    elif temp == 7:
                        dao.delete_student_by_id(id)
                        Group = text.upper()
                        dao.add_new_student(FIO[0], FIO[1], Group, id, IDT)
                        temp = 0
                    elif temp == 8:
                        dao.delete_student_by_id(id)
                        IDT = text.replace("https://t.me/", '')
                        dao.add_new_student(FIO[0], FIO[1], Group, id, IDT)
                        temp = 0
                    elif text.lower() == '/list' or text.lower() == '/ls':
                        main.send_msg(id, self.list_to_str(dao))
                    elif text.lower() == '/new':
                        # первая ошибка - отсутствие проверки на ввод формата группы
                        main.send_msg(id,
                                      "Введите в одну строку через пробел имя, фамилию, номер группы, id-vk и id-telegram:")
                        temp = 9
                    elif temp == 9 and text.lower() != '/undo':
                        text = text.split(' ')
                        while len(text) < 5:
                            text.append('')
                        dao.add_new_student(text[0], text[1], text[2], text[3], text[4])
                        main.send_msg(id,
                                      "Пользователь успешно добавлен!\nЧтобы отменить добавление, напишите /undo.\n\n Чтобы посмотреть список студентов, напишите /ls или /list.")
                    elif temp == 9 and text.lower() == '/undo':
                        if dao.delete_student_by_id(self.find_students(dao,
                                                                       id)) != '&#10060;Данный пользователь не найден. Пожалуйста проверьте введенные данные.':
                            main.send_msg(id, "Запись о студенте была успешно удалена.")
                        else:
                            main.send_msg(id, '&#10060;Данный пользователь не найден.')
                        temp = 0
                    elif text.lower() == '/msg':
                        main.send_msg(id, "&#9997; Напишите ваше новое сообщение:")
                        temp = 10
                    elif temp == 10:
                        buff += text
                        main.send_msg(id,
                                      "Напишите ID-VK человека, которому адресовано сообщение.\n\nАктуальный список можно посмотреть в /ls или /list.")
                        buff = ''
                        temp = 11
                    # вторая ошибка - отсутствие проверки на ввод id-vk
                    elif temp == 11:
                        main.send_msg(int(text), buff)
                        main.send_msg(id, "Ваше сообщение было успешно отправлено!")
                        temp = 0
                    elif text.lower() == '/del' or text.lower() == '/delete':
                        main.send_msg(id,
                                      'Напишите ID-VK пользователя, которого желаете удалить из списка студентов.\n\nАктуальный список можно посмотреть в /ls или /list.')
                        temp = 12
                    elif temp == 12:
                        num_stud = self.find_students(dao, text)
                        if num_stud != '&#10060;Данный пользователь не найден. Пожалуйста проверьте введенные данные.':
                            dao.delete_student_by_id(num_stud)
                            main.send_msg(id, 'Студент был успешно удален из списка.')
                        else:
                            main.send_msg(id,
                                          '&#10060;Данный пользователь не найден. Пожалуйста проверьте введенные данные.')
                        temp = 0
                    else:
                        main.send_msg(id, 'Я вас не понимаю&#128532;, повторите свой запрос.\n\nСписок команд – /help.')


if __name__ == "__main__":
    main = Main()
    main.events()
