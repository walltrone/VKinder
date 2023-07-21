# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools


class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.users = []

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):

        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    if self.params is None:
                        self.params = self.api.get_profile_info(event.user_id)
                        empty_data = [
                            key for key, value in self.params.items() if value is None]
                    self.message_send(
                        event.user_id, f'Здравствуй {self.params["name"]}')
                    if empty_data:
                        data = {
                            'bdate': 'год рождения (1901-2022)',
                            'home_town': 'город',
                            'sex': 'пол (м/ж)',
                            'relation': 'семейное положение',
                        }
                        key = empty_data.pop()
                        self.message_send(
                            event.user_id, f'Пожалуйста, назовите {data[key]}')

                elif self.params is not None and self.params[key] is None:
                    match key, command:
                        case 'bdate', command:
                            if command.isdigit() and 2023 > int(command) > 1900:
                                self.params[key] = f'0.0.{command}'
                                self.message_send(event.user_id, 'Принято!')
                            else:
                                self.message_send(
                                    event.user_id, 'неверное значение, попробуйте еще раз')
                        case 'sex', ('м' | 'ж'):
                            self.params[key] = {'м': 2, 'ж': 1}[command]
                            self.message_send(event.user_id, 'Принято!')
                        case ('relation' | 'home_town'), command:
                            self.params[key] = command
                            self.message_send(event.user_id, 'Принято!')
                        case _:
                            self.message_send(
                                event.user_id, 'неверное значение, попробуйте еще раз')
                    if self.params[key] is not None and empty_data:
                        key = empty_data.pop()
                        self.message_send(
                            event.user_id, f'Пожалуйста, назовите {data[key]}')
                else:
                    if self.params is not None and command == 'поиск':
                        if self.users == []:
                            self.users = self.api.search_users(self.params)
                        user = self.users.pop()

                        # здесь логика дял проверки бд
                        photos_user = self.api.get_photos(user['id'])

                        attachment = ''
                        for num, photo in enumerate(photos_user):
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                            if num == 2:
                                break
                        self.message_send(event.user_id,
                                          f'Встречайте {user["name"]}',
                                          attachment=attachment
                                          )
                        # здесь логика для добавленяи в бд
                    elif command == 'пока':
                        self.message_send(event.user_id, 'До свидания!')
                    else:
                        self.message_send(event.user_id, '''Инструкции и доступные команды:
                                          "Привет" - приветствие, возможно придется ответить на \
                                          несколько вопросов (следует начинать с этого)
                                          "Поиск" - искать анкеты (без приветствия не работает)
                                          "Пока" - попрощаться)''')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
