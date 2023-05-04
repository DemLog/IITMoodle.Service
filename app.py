from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/')
def index():
    username = request.args.get('username')
    password = request.args.get('password')
    user_data = get_user_data(username, password)
    return user_data


def get_logintoken(session):
    response = session.get('https://eu.iit.csu.ru/login/index.php/')
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.find('input', {'name': 'logintoken'}).get('value')


def get_user(session, username, password, logintoken, ancho=""):
    data_auth = {
        "ancho": ancho,
        "logintoken": logintoken,
        "username": username,
        "password": password
    }
    response = session.post('https://eu.iit.csu.ru/login/index.php/', data=data_auth)
    return response


def get_user_data(username, password):
    session = requests.Session()
    logintoken = get_logintoken(session)
    user = get_user(session, username, password, logintoken)
    context_auth = BeautifulSoup(user.text, 'lxml')
    error_message = context_auth.find('a', {'id': 'loginerrormessage'})
    if error_message is not None:
        return {'error_message': error_message.contents[0]}
    else:
        return get_user_details(session)


def get_user_details(user_session):
    params = {
        'first_name': None,
        'last_name': None,
        'patronymic': 'Отчество',
        'email': 'Адрес электронной почты',
        'country': 'Страна',
        'city': 'Город',
        'status': 'Статус',
        'study_group': 'Учебная группа',
        'direction': 'Направление обучения',
        'profile': 'Профиль',
        'form_study': 'Форма обучения'
    }

    user = user_session.get('https://eu.iit.csu.ru/user/profile.php')
    user_data = BeautifulSoup(user.text, 'lxml')

    # Получение имени и фамилии
    full_name = user_data.find('div', {'class': 'page-header-headings'}).find('h1').contents
    params['last_name'], params['first_name'] = full_name[0].split(' ')

    detailed_info = user_data.find('div', {'class': 'profile_tree'}).find('section').find('ul').find_all('dd')
    detailed_info_header = user_data.find('div', {'class': 'profile_tree'}).find('section').find('ul').find_all('dt')
    for key, value in params.items():
        for x in range(0, len(detailed_info_header)):
            if detailed_info_header[x].contents[0] == value:
                if key == 'email':
                    params[key] = detailed_info[x].find('a').contents[0]
                else:
                    params[key] = detailed_info[x].contents[0].strip()

    return params


if __name__ == '__main__':
    app.run()