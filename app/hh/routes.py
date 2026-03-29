from flask import redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from app.hh import bp
from app.models.platform_connection import PlatformConnection, ResumePublication
from app.models.resume import Resume
from app import db
from datetime import datetime

from app.services import hh_api
from app.services.encryption_service import encrypt_token


@bp.route('/connect')
@login_required
def connect():
    state = hh_api.generate_state()
    session['hh_oauth_state'] = state
    session['hh_oauth_user_id'] = current_user.id
    auth_url = hh_api.get_auth_url(state=state)
    return redirect(auth_url)


@bp.route('/oauth-callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        flash(f'Ошибка авторизации на HH.ru: {error}', 'danger')
        return redirect(url_for('integrations.platforms'))
    
    if not code:
        flash('Ошибка авторизации: код не получен', 'danger')
        return redirect(url_for('integrations.platforms'))
    
    stored_state = session.get('hh_oauth_state')
    if not stored_state or stored_state != state:
        flash('Ошибка безопасности: неверный state параметр', 'danger')
        return redirect(url_for('integrations.platforms'))
    
    user_id = session.get('hh_oauth_user_id')
    if not user_id:
        flash('Сессия истекла, попробуйте снова', 'danger')
        return redirect(url_for('integrations.platforms'))
    
    session.pop('hh_oauth_state', None)
    session.pop('hh_oauth_user_id', None)
    
    token_data = hh_api.exchange_code_for_token(code)
    
    if not token_data:
        flash('Не удалось получить токен от HH.ru', 'danger')
        return redirect(url_for('integrations.platforms'))
    
    connection = PlatformConnection.query.filter_by(
        user_id=user_id,
        platform='hh'
    ).first()
    
    if not connection:
        connection = PlatformConnection(
            user_id=user_id,
            platform='hh'
        )
        db.session.add(connection)
    
    connection.access_token = token_data['access_token']
    connection.set_refresh_token(token_data['refresh_token'])
    connection.expires_at = token_data['expires_at']
    connection.is_active = True
    
    db.session.commit()
    
    flash('Успешно подключено к HH.ru!', 'success')
    return redirect(url_for('integrations.platforms'))


@bp.route('/status')
@login_required
def status():
    connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform='hh'
    ).first()
    
    if not connection:
        return jsonify({
            'connected': False,
            'message': 'Аккаунт HH.ru не подключен'
        })
    
    is_valid = connection.is_token_valid()
    
    return jsonify({
        'connected': connection.is_active and is_valid,
        'is_active': connection.is_active,
        'token_valid': is_valid,
        'expires_at': connection.expires_at.isoformat() if connection.expires_at else None,
        'hh_resume_id': connection.hh_resume_id,
        'external_resume_url': connection.external_resume_url
    })


@bp.route('/publish/<int:resume_id>', methods=['POST'])
@login_required
def publish(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    
    connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform='hh'
    ).first()
    
    if not connection or not connection.is_active:
        return jsonify({'error': 'Сначала подключитесь к HH.ru'}), 400
    
    access_token = hh_api.ensure_valid_token(connection)
    
    if not access_token:
        return jsonify({'error': 'Токен истек, переподключитесь к HH.ru'}), 401
    
    publication = ResumePublication(
        resume_id=resume.id,
        platform='hh',
        status='processing'
    )
    db.session.add(publication)
    db.session.commit()
    
    try:
        adapted_data = hh_api.adapt_resume_for_hh(resume)
        
        if connection.hh_resume_id:
            result = hh_api.update_resume(access_token, connection.hh_resume_id, adapted_data)
            if result.get('success'):
                pub_result = hh_api.publish_resume(access_token, connection.hh_resume_id)
                if not pub_result.get('success'):
                    result = pub_result
        else:
            result = hh_api.create_resume(access_token, adapted_data)
        
        if result.get('success'):
            publication.status = 'published'
            publication.published_at = datetime.utcnow()
            if result.get('data'):
                resume_id_hh = str(result['data'].get('id', ''))
                publication.external_id = resume_id_hh
                publication.external_url = f"https://hh.ru/resume/{resume_id_hh}"
                connection.hh_resume_id = resume_id_hh
                connection.external_resume_url = publication.external_url
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Резюме опубликовано на HH.ru!',
                'url': publication.external_url
            })
        else:
            publication.status = 'failed'
            publication.error_message = result.get('error', 'Неизвестная ошибка')
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': publication.error_message
            }), 400
            
    except Exception as e:
        publication.status = 'failed'
        publication.error_message = str(e)
        db.session.commit()
        
        return jsonify({'error': str(e)}), 500


@bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform='hh'
    ).first()
    
    if connection:
        connection.is_active = False
        connection.access_token = None
        connection.refresh_token = None
        connection.refresh_token_encrypted = None
        db.session.commit()
        
    return jsonify({'success': True, 'message': 'Отключено от HH.ru'})
