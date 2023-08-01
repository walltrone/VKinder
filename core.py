from datetime import datetime

import re

import vk_api

from config import acces_token


class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)
        self.offset = 0

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation,home_town'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id':  info['id'],
                     'bdate': info['bdate'] if re.search(r'\d+\.\d+\.\d{4}', info['bdate']) else None,
                     'sex': info['sex'] or None,
                     'city': info['city']['id'] if 'city' in info else None,
                     'relation': info['relation'] or None,
                     'offset': 0
                     }
        return user_info

    def get_city_id(self, city_name):
        cities = self.api.method('database.getCities',
                                 {'q': city_name,
                                  'count': 1,
                                  'need_all': 1
                                  }
                                 )
        return cities['items'][0]['id']

    def search_users(self, params):

        sex = params['sex'] % 2 + 1
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5 if age - 5 > 0 else age
        age_to = age + 5 if age + 5 < 120 else 120
        offset = params['offset']

        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info()
    users = bot.search_users(params)
    print(bot.get_photos(users[2]['id']))
