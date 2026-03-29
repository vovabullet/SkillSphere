from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.admin import bp
from app.models.api_settings import ApiSettings
from app import db
import os


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещён. Требуются права администратора.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def get_platform_config(platform):
    db_settings = ApiSettings.get_settings(platform)
    if db_settings and db_settings.client_id:
        return {
            'client_id': db_settings.client_id,
            'client_secret': db_settings.client_secret,
            'redirect_uri': db_settings.redirect_uri,
            'source': 'database'
        }
    
    prefix = platform.upper()
    return {
        'client_id': os.environ.get(f'{prefix}_CLIENT_ID', ''),
        'client_secret': os.environ.get(f'{prefix}_CLIENT_SECRET', ''),
        'redirect_uri': os.environ.get(f'{prefix}_REDIRECT_URI', ''),
        'source': 'environment'
    }


@bp.route('/')
@login_required
@admin_required
def index():
    hh_config = get_platform_config('hh')
    superjob_config = get_platform_config('superjob')
    
    hh_configured = bool(hh_config['client_id']) and bool(hh_config['client_secret'])
    superjob_configured = bool(superjob_config['client_id']) and bool(superjob_config['client_secret'])
    
    gigachat_settings = ApiSettings.get_settings('gigachat')
    gigachat_configured = gigachat_settings is not None and bool(gigachat_settings.client_secret)
    
    return render_template('admin/index.html',
                         hh_configured=hh_configured,
                         superjob_configured=superjob_configured,
                         gigachat_configured=gigachat_configured,
                         title='Панель администратора')


@bp.route('/api-settings')
@login_required
@admin_required
def api_settings():
    hh_settings = ApiSettings.get_settings('hh')
    superjob_settings = ApiSettings.get_settings('superjob')
    gigachat_settings = ApiSettings.get_settings('gigachat')
    
    settings = {
        'hh': {
            'client_id': hh_settings.client_id if hh_settings else '',
            'client_secret': hh_settings.client_secret if hh_settings else '',
            'redirect_uri': hh_settings.redirect_uri if hh_settings else '',
            'has_db_config': hh_settings is not None and bool(hh_settings.client_id)
        },
        'superjob': {
            'client_id': superjob_settings.client_id if superjob_settings else '',
            'client_secret': superjob_settings.client_secret if superjob_settings else '',
            'redirect_uri': superjob_settings.redirect_uri if superjob_settings else '',
            'has_db_config': superjob_settings is not None and bool(superjob_settings.client_id)
        },
        'gigachat': {
            'api_key': gigachat_settings.client_secret if gigachat_settings else '',
            'has_db_config': gigachat_settings is not None and bool(gigachat_settings.client_secret)
        }
    }
    
    return render_template('admin/api_settings.html',
                         settings=settings,
                         title='Настройки API')


@bp.route('/api-settings/<platform>', methods=['POST'])
@login_required
@admin_required
def save_api_settings(platform):
    if platform not in ['hh', 'superjob', 'gigachat']:
        flash('Неизвестная платформа', 'danger')
        return redirect(url_for('admin.api_settings'))
    
    if platform == 'gigachat':
        api_key = request.form.get('api_key', '').strip()
        
        if not api_key:
            flash('API ключ GigaChat обязателен', 'danger')
            return redirect(url_for('admin.api_settings'))
        
        settings = ApiSettings.query.filter_by(platform=platform).first()
        
        if not settings:
            settings = ApiSettings(platform=platform)
            db.session.add(settings)
        
        settings.client_secret = api_key
        settings.updated_by_id = current_user.id
        settings.is_active = True
        
        db.session.commit()
        
        flash('Настройки GigaChat сохранены', 'success')
        return redirect(url_for('admin.api_settings'))
    
    client_id = request.form.get('client_id', '').strip()
    client_secret = request.form.get('client_secret', '').strip()
    redirect_uri = request.form.get('redirect_uri', '').strip()
    
    if not client_id or not client_secret:
        flash('Client ID и Client Secret обязательны', 'danger')
        return redirect(url_for('admin.api_settings'))
    
    settings = ApiSettings.query.filter_by(platform=platform).first()
    
    if not settings:
        settings = ApiSettings(platform=platform)
        db.session.add(settings)
    
    settings.client_id = client_id
    settings.client_secret = client_secret
    settings.redirect_uri = redirect_uri
    settings.updated_by_id = current_user.id
    settings.is_active = True
    
    db.session.commit()
    
    platform_name = 'HH.ru' if platform == 'hh' else 'SuperJob'
    flash(f'Настройки {platform_name} сохранены', 'success')
    return redirect(url_for('admin.api_settings'))


@bp.route('/api-settings/<platform>/delete', methods=['POST'])
@login_required
@admin_required
def delete_api_settings(platform):
    if platform not in ['hh', 'superjob', 'gigachat']:
        flash('Неизвестная платформа', 'danger')
        return redirect(url_for('admin.api_settings'))
    
    settings = ApiSettings.query.filter_by(platform=platform).first()
    if settings:
        db.session.delete(settings)
        db.session.commit()
        platform_name = 'GigaChat' if platform == 'gigachat' else platform.upper()
        flash(f'Настройки {platform_name} удалены', 'info')
    
    return redirect(url_for('admin.api_settings'))


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(current_password):
            flash('Неверный текущий пароль', 'danger')
            return redirect(url_for('admin.change_password'))
        
        if len(new_password) < 6:
            flash('Новый пароль должен быть не менее 6 символов', 'danger')
            return redirect(url_for('admin.change_password'))
        
        if new_password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('admin.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Пароль успешно изменён', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/change_password.html', title='Смена пароля')
