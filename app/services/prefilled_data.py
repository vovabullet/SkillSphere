JOB_POSITIONS = {
    'analyst': {
        'title': 'Аналитик данных',
        'full_name': 'Михаил',
        'summary': 'Опытный аналитик с навыками работы с большими данными, SQL и Python. Умею находить инсайты в данных и превращать их в бизнес-рекомендации.',
        'skills': [
            {'name': 'SQL', 'level': 90},
            {'name': 'Python', 'level': 85},
            {'name': 'Excel', 'level': 95},
            {'name': 'Power BI', 'level': 80},
            {'name': 'Tableau', 'level': 75},
            {'name': 'Статистический анализ', 'level': 80},
            {'name': '1C', 'level': 70},
        ],
        'experience': [
            {
                'company': 'ООО "Технологии будущего"',
                'position': 'Младший аналитик данных',
                'start_date': '2022-01',
                'end_date': '',
                'description': 'Анализ продаж, построение отчетов, работа с SQL базами данных'
            }
        ],
        'education': [
            {
                'institution': 'Московский государственный университет',
                'degree': 'Бакалавр экономики',
                'start_date': '2018',
                'end_date': '2022',
                'description': ''
            }
        ]
    },
    'sales': {
        'title': 'Менеджер по продажам',
        'full_name': 'Михаил',
        'summary': 'Энергичный менеджер по продажам с опытом работы в B2B и B2C сегментах. Превышаю планы продаж и выстраиваю долгосрочные отношения с клиентами.',
        'skills': [
            {'name': 'Активные продажи', 'level': 95},
            {'name': 'Переговоры', 'level': 90},
            {'name': 'CRM системы', 'level': 85},
            {'name': 'Холодные звонки', 'level': 90},
            {'name': 'Презентации', 'level': 85},
            {'name': 'Работа с возражениями', 'level': 90},
            {'name': 'Excel', 'level': 75},
        ],
        'experience': [
            {
                'company': 'ТОП Продажи',
                'position': 'Менеджер по продажам',
                'start_date': '2021-06',
                'end_date': '',
                'description': 'Активные продажи, работа с клиентской базой, выполнение плана продаж на 120%'
            }
        ],
        'education': [
            {
                'institution': 'Российский экономический университет',
                'degree': 'Бакалавр менеджмента',
                'start_date': '2017',
                'end_date': '2021',
                'description': ''
            }
        ]
    }
}

DEFAULT_CONTACT = {
    'email': 'mikhail@example.com',
    'phone': '+7 (999) 123-45-67',
    'location': 'Москва, Россия'
}

def get_prefilled_data(position_key='analyst'):
    position = JOB_POSITIONS.get(position_key, JOB_POSITIONS['analyst'])
    return {
        **position,
        **DEFAULT_CONTACT
    }

def get_all_positions():
    return [
        {'key': 'analyst', 'name': 'Аналитик данных'},
        {'key': 'sales', 'name': 'Менеджер по продажам'}
    ]
