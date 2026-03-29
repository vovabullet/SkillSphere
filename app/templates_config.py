"""
Конфигурация шаблонов резюме для разных профессий и индустрий.
"""

RESUME_TEMPLATES = {
    'classic': {
        'name': 'Классический',
        'description': 'Универсальный стиль для любой профессии',
        'font': 'Arial',
        'primary_color': '#2c3e50',
        'secondary_color': '#34495e',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'it_developer': {
        'name': 'IT / Разработчик',
        'description': 'Современный технический стиль',
        'font': 'Courier New',
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'marketing': {
        'name': 'Маркетинг',
        'description': 'Креативный и яркий дизайн',
        'font': 'Georgia',
        'primary_color': '#f093fb',
        'secondary_color': '#f5576c',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'engineering': {
        'name': 'Инженерия',
        'description': 'Строгий профессиональный стиль',
        'font': 'Times New Roman',
        'primary_color': '#2d98da',
        'secondary_color': '#3867d6',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'management': {
        'name': 'Менеджмент',
        'description': 'Элегантный деловой стиль',
        'font': 'Verdana',
        'primary_color': '#8e44ad',
        'secondary_color': '#9b59b6',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'creative': {
        'name': 'Креативные профессии',
        'description': 'Художественный и необычный дизайн',
        'font': 'Comic Sans MS',
        'primary_color': '#ee5a6f',
        'secondary_color': '#f29263',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'finance': {
        'name': 'Финансы / Бухгалтерия',
        'description': 'Консервативный надежный стиль',
        'font': 'Arial',
        'primary_color': '#0c2461',
        'secondary_color': '#1e3799',
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True
        }
    },
    'sales': {
        'name': 'Продажи',
        'description': 'Энергичный убедительный стиль',
        'font': 'Tahoma',
        'primary_color': '#e74c3c',
        'secondary_color': '#c0392b',
        'sections': {
            'summary': True,
            'experience': True,
            'education': False,
            'skills': True
        }
    }
}

AVAILABLE_FONTS = [
    'Arial',
    'Times New Roman',
    'Georgia',
    'Verdana',
    'Tahoma',
    'Courier New',
    'Comic Sans MS',
    'Trebuchet MS',
    'Lucida Console'
]

def get_template(template_name):
    """Получить конфигурацию шаблона по имени"""
    return RESUME_TEMPLATES.get(template_name, RESUME_TEMPLATES['classic'])

def get_all_templates():
    """Получить список всех доступных шаблонов"""
    return RESUME_TEMPLATES
