"""
Модуль для работы с GigaChat API для улучшения резюме.

Этот модуль предоставляет функции для анализа, улучшения и генерации
текста резюме с использованием искусственного интеллекта GigaChat.
"""

import os
import requests
import uuid
from typing import Optional
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SYSTEM_PROMPT = "Ты — карьерный консультант. Помогай улучшать резюме. Давай конкретные рекомендации."

def _get_gigachat_credentials() -> str:
    """
    Получает API ключ GigaChat из базы данных или переменных окружения.
    
    Returns:
        str: API ключ GigaChat
        
    Raises:
        ValueError: Если ключ не настроен
    """
    try:
        from app.models.api_settings import ApiSettings
        settings = ApiSettings.get_settings('gigachat')
        if settings and settings.client_secret:
            return settings.client_secret
    except Exception:
        pass
    
    credentials = os.environ.get('GIGACHAT_KEY')
    if credentials:
        return credentials
    
    raise ValueError("API ключ GigaChat не настроен. Добавьте его в админ-панели или в переменных окружения")


def _get_access_token() -> str:
    """
    Получает access token для работы с GigaChat API.
    
    Returns:
        str: Access token
        
    Raises:
        ValueError: Если GIGACHAT_KEY не установлен
        Exception: При ошибках получения токена
    """
    credentials = _get_gigachat_credentials()
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {credentials}'
    }
    
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        raise Exception(f"Ошибка получения токена: {str(e)}")


def _send_chat_request(messages: list, temperature: float = 0.5, max_tokens: int = 500) -> str:
    """
    Отправляет запрос к GigaChat API и возвращает ответ.
    
    Args:
        messages: Список сообщений для отправки
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов
        
    Returns:
        str: Ответ от API
    """
    access_token = _get_access_token()
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    payload = {
        "model": "GigaChat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Ошибка запроса к API: {str(e)}")


def analyze_resume(resume_text: str) -> str:
    """
    Анализирует резюме и возвращает 3-5 рекомендаций по улучшению.
    
    Функция отправляет текст резюме в GigaChat API для анализа и получения
    конкретных рекомендаций по улучшению. Персональные данные (ФИО, паспорт, ИНН)
    должны быть удалены перед отправкой.
    
    Args:
        resume_text (str): Текст резюме для анализа (без персональных данных)
        
    Returns:
        str: Список рекомендаций по улучшению резюме (3-5 пунктов)
        
    Raises:
        ValueError: Если resume_text пустой или GIGACHAT_KEY не установлен
        Exception: При ошибках взаимодействия с API
        
    Example:
        >>> recommendations = analyze_resume("Опыт работы: 5 лет программистом...")
        >>> print(recommendations)
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Текст резюме не может быть пустым")
    
    try:
        prompt = f"""Проанализируй следующее резюме и дай 3-5 конкретных рекомендаций по его улучшению.
Сосредоточься на структуре, содержании и профессиональной подаче информации.

Резюме:
{resume_text}

Дай рекомендации в виде нумерованного списка."""

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return _send_chat_request(messages, temperature=0.5, max_tokens=500)
        
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Ошибка при анализе резюме: {str(e)}")


def improve_text(text: str, job_title: Optional[str] = None) -> str:
    """
    Улучшает формулировку текста, делая его более профессиональным.
    
    Функция принимает текст и улучшает его формулировку, делая более
    профессиональной и подходящей для резюме. Если указана должность,
    учитывает специфику профессии при улучшении текста.
    
    Args:
        text (str): Текст для улучшения
        job_title (str, optional): Желаемая должность для учета специфики профессии
        
    Returns:
        str: Улучшенный профессиональный текст
        
    Raises:
        ValueError: Если text пустой или GIGACHAT_KEY не установлен
        Exception: При ошибках взаимодействия с API
        
    Example:
        >>> improved = improve_text("Делал сайты", "Frontend разработчик")
        >>> print(improved)
        "Разрабатывал веб-приложения с использованием современных технологий..."
    """
    if not text or not text.strip():
        raise ValueError("Текст для улучшения не может быть пустым")
    
    try:
        if job_title:
            prompt = f"""Улучши следующий текст для резюме, сделай его более профессиональным и подходящим для должности "{job_title}".
Учитывай специфику профессии и используй соответствующую терминологию.

Исходный текст:
{text}

Верни только улучшенный текст без дополнительных комментариев."""
        else:
            prompt = f"""Улучши следующий текст для резюме, сделай его более профессиональным и структурированным.

Исходный текст:
{text}

Верни только улучшенный текст без дополнительных комментариев."""

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return _send_chat_request(messages, temperature=0.5, max_tokens=500)
        
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Ошибка при улучшении текста: {str(e)}")


def validate_job_title(job_title: str) -> dict:
    """
    Проверяет, является ли введенная должность адекватной и реальной.
    
    Args:
        job_title: Название должности для проверки
        
    Returns:
        dict: {'valid': bool, 'message': str, 'normalized_title': str}
    """
    if not job_title or not job_title.strip():
        return {'valid': False, 'message': 'Название должности не может быть пустым', 'normalized_title': ''}
    
    if len(job_title.strip()) < 3:
        return {'valid': False, 'message': 'Название должности слишком короткое', 'normalized_title': ''}
    
    try:
        prompt = f"""Проверь, является ли "{job_title}" реальной профессией или должностью.

Ответь строго в формате JSON:
{{"valid": true/false, "message": "причина если невалидно", "normalized_title": "нормализованное название должности на русском"}}

Примеры валидных должностей: Программист, Менеджер по продажам, Дизайнер, Врач, Учитель, Инженер, Бухгалтер.
Примеры НЕвалидных: абракадабра, asdfgh, 12345, случайный набор букв.

Если должность валидна, normalized_title должен содержать корректное название должности на русском языке."""

        messages = [
            {
                "role": "system",
                "content": "Ты — эксперт по профессиям. Отвечай только в формате JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = _send_chat_request(messages, temperature=0.1, max_tokens=200)
        
        import json
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
                return result
        except:
            pass
        
        return {'valid': True, 'message': '', 'normalized_title': job_title.strip()}
        
    except Exception as e:
        return {'valid': True, 'message': '', 'normalized_title': job_title.strip()}


def generate_resume_data(job_title: str) -> dict:
    """
    Генерирует данные для резюме на основе должности.
    
    Args:
        job_title: Название должности
        
    Returns:
        dict: Данные для заполнения резюме (summary, skills)
    """
    if not job_title or not job_title.strip():
        raise ValueError("Название должности не может быть пустым")
    
    try:
        prompt = f"""Создай профессиональные данные для резюме на должность "{job_title}".

Ответь строго в формате JSON:
{{
    "title": "точное название должности",
    "summary": "профессиональное описание О себе (3-4 предложения, от первого лица)",
    "skills": ["навык1", "навык2", "навык3", "навык4", "навык5"]
}}

Требования:
- summary должен быть профессиональным, от первого лица
- skills - 5 ключевых навыков для этой должности
- Все на русском языке"""

        messages = [
            {
                "role": "system",
                "content": "Ты — карьерный консультант. Создаёшь профессиональные резюме. Отвечай только в формате JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = _send_chat_request(messages, temperature=0.7, max_tokens=600)
        
        import json
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
                return result
        except:
            pass
        
        return {
            'title': job_title,
            'summary': f'Специалист в области {job_title} с опытом работы.',
            'skills': ['Коммуникабельность', 'Ответственность', 'Работа в команде']
        }
        
    except Exception as e:
        raise Exception(f"Ошибка при генерации данных: {str(e)}")


def generate_summary(experience: str, job_title: str) -> str:
    """
    Генерирует профессиональное summary (раздел "О себе") на основе опыта работы и желаемой должности.
    
    Функция создает краткое профессиональное резюме (summary), которое подчеркивает
    ключевые навыки и опыт, релевантные для желаемой должности.
    
    Args:
        experience (str): Описание опыта работы и навыков
        job_title (str): Желаемая должность
        
    Returns:
        str: Профессиональное summary для раздела "О себе"
        
    Raises:
        ValueError: Если experience или job_title пустые, или GIGACHAT_KEY не установлен
        Exception: При ошибках взаимодействия с API
        
    Example:
        >>> summary = generate_summary(
        ...     "5 лет опыта в Python, работал над веб-проектами",
        ...     "Senior Python Developer"
        ... )
        >>> print(summary)
        "Опытный Python-разработчик с 5-летним стажем..."
    """
    if not experience or not experience.strip():
        raise ValueError("Описание опыта не может быть пустым")
    
    if not job_title or not job_title.strip():
        raise ValueError("Название должности не может быть пустым")
    
    try:
        prompt = f"""Создай профессиональное summary (раздел "О себе") для резюме на должность "{job_title}".

Опыт и навыки кандидата:
{experience}

Требования к summary:
- Краткое (3-5 предложений)
- Подчеркивает ключевые навыки и достижения
- Соответствует желаемой должности
- Профессиональный тон

Верни только текст summary без заголовков и дополнительных комментариев."""

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return _send_chat_request(messages, temperature=0.5, max_tokens=500)
        
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Ошибка при генерации summary: {str(e)}")
