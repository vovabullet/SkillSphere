"""
Пакет services содержит различные сервисы для работы приложения.
"""

from .gigachat_service import analyze_resume, improve_text, generate_summary

__all__ = ['analyze_resume', 'improve_text', 'generate_summary']
