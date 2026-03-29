from flask import render_template
from flask_login import current_user, login_required
from app.main import bp
from app.models.resume import Resume

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/examples')
def examples():
    return render_template('main/examples.html')

@bp.route('/examples/<profession>')
def example_profession(profession):
    examples_data = {
        'sales-manager': {
            'title': 'Менеджер по продажам',
            'icon': '💼',
            'full_name': 'Иванов Алексей Петрович',
            'email': 'ivanov@email.ru',
            'phone': '+7 (999) 123-45-67',
            'location': 'Москва',
            'summary': 'Опытный менеджер по продажам с 5-летним стажем работы в B2B и B2C сегментах. Успешно увеличивал объемы продаж на 30-50% ежегодно. Владею техниками активных продаж, ведения переговоров и работы с возражениями. Имею опыт управления командой из 5 человек.',
            'experience': [
                {'company': 'ООО "ТехноПром"', 'position': 'Старший менеджер по продажам', 'period': '2021 - настоящее время', 'description': 'Увеличил клиентскую базу на 40%. Выполнял план продаж на 120%. Обучал новых сотрудников.'},
                {'company': 'ЗАО "СтройМаркет"', 'position': 'Менеджер по продажам', 'period': '2019 - 2021', 'description': 'Работа с корпоративными клиентами. Заключение договоров на сумму более 50 млн руб.'}
            ],
            'education': [{'institution': 'РЭУ им. Г.В. Плеханова', 'degree': 'Менеджмент', 'year': '2019'}],
            'skills': ['Активные продажи', 'CRM-системы', 'Ведение переговоров', 'MS Office', '1С']
        },
        'programmer': {
            'title': 'Программист',
            'icon': '💻',
            'full_name': 'Сидоров Дмитрий Андреевич',
            'email': 'sidorov.dev@email.ru',
            'phone': '+7 (999) 987-65-43',
            'location': 'Санкт-Петербург',
            'summary': 'Full-stack разработчик с 4-летним опытом. Специализируюсь на Python/Django и React. Участвовал в разработке высоконагруженных веб-приложений. Имею опыт работы в Agile-командах.',
            'experience': [
                {'company': 'IT-компания "Digital Solutions"', 'position': 'Full-stack разработчик', 'period': '2022 - настоящее время', 'description': 'Разработка микросервисной архитектуры. Оптимизация производительности БД. Code review.'},
                {'company': 'Стартап "WebApp"', 'position': 'Junior Python Developer', 'period': '2020 - 2022', 'description': 'Разработка REST API. Написание unit-тестов. Работа с PostgreSQL.'}
            ],
            'education': [{'institution': 'ИТМО', 'degree': 'Программная инженерия', 'year': '2020'}],
            'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'Docker', 'Git']
        },
        'accountant': {
            'title': 'Бухгалтер',
            'icon': '📊',
            'full_name': 'Петрова Елена Сергеевна',
            'email': 'petrova.es@email.ru',
            'phone': '+7 (999) 555-44-33',
            'location': 'Екатеринбург',
            'summary': 'Главный бухгалтер с опытом работы более 7 лет. Ведение полного цикла бухгалтерского и налогового учета. Успешное прохождение налоговых проверок. Опыт работы с МСФО.',
            'experience': [
                {'company': 'ООО "ФинансГрупп"', 'position': 'Главный бухгалтер', 'period': '2020 - настоящее время', 'description': 'Ведение бухгалтерского учета. Подготовка отчетности. Работа с налоговыми органами.'},
                {'company': 'ИП Козлов', 'position': 'Бухгалтер', 'period': '2017 - 2020', 'description': 'Расчет заработной платы. Ведение кассовых операций.'}
            ],
            'education': [{'institution': 'УрГЭУ', 'degree': 'Бухгалтерский учет и аудит', 'year': '2017'}],
            'skills': ['1С:Бухгалтерия', 'Налоговый учет', 'МСФО', 'Excel', 'Консультант+']
        },
        'lawyer': {
            'title': 'Юрист',
            'icon': '⚖️',
            'full_name': 'Козлова Анна Викторовна',
            'email': 'kozlova.law@email.ru',
            'phone': '+7 (999) 222-11-00',
            'location': 'Москва',
            'summary': 'Юрист с 6-летним опытом в области корпоративного права. Сопровождение сделок M&A. Успешное представление интересов клиентов в арбитражных судах.',
            'experience': [
                {'company': 'Юридическая фирма "Право и Закон"', 'position': 'Старший юрист', 'period': '2021 - настоящее время', 'description': 'Корпоративное право. Сопровождение сделок. Судебное представительство.'},
                {'company': 'ООО "ЮрКонсалт"', 'position': 'Юрист', 'period': '2018 - 2021', 'description': 'Подготовка договоров. Претензионная работа.'}
            ],
            'education': [{'institution': 'МГУ им. М.В. Ломоносова', 'degree': 'Юриспруденция', 'year': '2018'}],
            'skills': ['Корпоративное право', 'Арбитраж', 'Договорная работа', 'Due Diligence', 'Консультант+']
        },
        'designer': {
            'title': 'Дизайнер',
            'icon': '🎨',
            'full_name': 'Морозова Ольга Игоревна',
            'email': 'morozova.design@email.ru',
            'phone': '+7 (999) 333-22-11',
            'location': 'Москва',
            'summary': 'UI/UX дизайнер с 4-летним опытом. Создаю удобные и красивые интерфейсы для веб и мобильных приложений. Работаю в тесном сотрудничестве с разработчиками и продуктовой командой.',
            'experience': [
                {'company': 'Digital Agency "Creative"', 'position': 'UI/UX дизайнер', 'period': '2021 - настоящее время', 'description': 'Проектирование интерфейсов. Создание дизайн-систем. Проведение UX-исследований.'},
                {'company': 'Фриланс', 'position': 'Графический дизайнер', 'period': '2020 - 2021', 'description': 'Разработка фирменного стиля. Дизайн полиграфии и социальных сетей.'}
            ],
            'education': [{'institution': 'Британская высшая школа дизайна', 'degree': 'Графический дизайн', 'year': '2020'}],
            'skills': ['Figma', 'Adobe Photoshop', 'Adobe Illustrator', 'Prototyping', 'Design Systems']
        },
        'engineer': {
            'title': 'Инженер',
            'icon': '🔧',
            'full_name': 'Николаев Сергей Владимирович',
            'email': 'nikolaev.eng@email.ru',
            'phone': '+7 (999) 444-55-66',
            'location': 'Новосибирск',
            'summary': 'Инженер-конструктор с 8-летним опытом в машиностроении. Разработка технической документации, 3D-моделирование, авторский надзор за производством.',
            'experience': [
                {'company': 'ОАО "МашПром"', 'position': 'Ведущий инженер-конструктор', 'period': '2019 - настоящее время', 'description': 'Разработка конструкторской документации. 3D-моделирование. Расчеты на прочность.'},
                {'company': 'ЗАО "ТехноСтрой"', 'position': 'Инженер-конструктор', 'period': '2016 - 2019', 'description': 'Проектирование металлоконструкций. Работа с заказчиками.'}
            ],
            'education': [{'institution': 'НГТУ', 'degree': 'Машиностроение', 'year': '2016'}],
            'skills': ['AutoCAD', 'SolidWorks', 'Компас-3D', 'Расчеты на прочность', 'ГОСТ']
        },
        'teacher': {
            'title': 'Учитель',
            'icon': '👨‍🏫',
            'full_name': 'Федорова Мария Александровна',
            'email': 'fedorova.teach@email.ru',
            'phone': '+7 (999) 777-88-99',
            'location': 'Казань',
            'summary': 'Учитель математики высшей категории с 10-летним стажем. Подготовка учеников к ОГЭ и ЕГЭ с результатами 80+ баллов. Победитель конкурса "Учитель года" 2022.',
            'experience': [
                {'company': 'Гимназия №1', 'position': 'Учитель математики', 'period': '2017 - настоящее время', 'description': 'Преподавание математики 5-11 классы. Подготовка к ОГЭ/ЕГЭ. Классное руководство.'},
                {'company': 'СОШ №45', 'position': 'Учитель математики', 'period': '2014 - 2017', 'description': 'Ведение уроков математики. Внеклассная работа.'}
            ],
            'education': [{'institution': 'КФУ', 'degree': 'Педагогическое образование (математика)', 'year': '2014'}],
            'skills': ['Методика преподавания', 'Подготовка к ЕГЭ', 'Работа с детьми', 'Интерактивные технологии']
        },
        'doctor': {
            'title': 'Врач',
            'icon': '🏥',
            'full_name': 'Смирнов Андрей Николаевич',
            'email': 'smirnov.doc@email.ru',
            'phone': '+7 (999) 111-22-33',
            'location': 'Москва',
            'summary': 'Врач-терапевт с 12-летним стажем. Кандидат медицинских наук. Специализация на диагностике и лечении заболеваний внутренних органов. Опыт работы в стационаре и поликлинике.',
            'experience': [
                {'company': 'Городская клиническая больница №1', 'position': 'Врач-терапевт', 'period': '2018 - настоящее время', 'description': 'Амбулаторный прием. Диагностика заболеваний. Ведение медицинской документации.'},
                {'company': 'Поликлиника №5', 'position': 'Участковый терапевт', 'period': '2012 - 2018', 'description': 'Прием пациентов. Профилактические осмотры. Диспансеризация.'}
            ],
            'education': [{'institution': 'Первый МГМУ им. И.М. Сеченова', 'degree': 'Лечебное дело', 'year': '2012'}],
            'skills': ['Диагностика', 'Терапия', 'УЗИ', 'ЭКГ', 'Медицинская документация']
        }
    }
    
    example = examples_data.get(profession)
    if not example:
        return render_template('main/examples.html')
    
    return render_template('main/example_detail.html', example=example, profession=profession)

@bp.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.updated_at.desc()).all()
    return render_template('main/dashboard.html', resumes=resumes)
