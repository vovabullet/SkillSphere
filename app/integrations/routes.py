from flask import render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.integrations import bp
from app.models.platform_connection import PlatformConnection, ResumePublication
from app.models.api_settings import ApiSettings
from app.models.resume import Resume
from app import db


@bp.route('/platforms')
@login_required
def platforms():
    hh_connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform='hh'
    ).first()
    
    superjob_connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform='superjob'
    ).first()
    
    hh_settings = ApiSettings.get_settings('hh')
    superjob_settings = ApiSettings.get_settings('superjob')
    
    platforms_data = {
        'hh': {
            'name': 'HH.ru',
            'description': 'Крупнейший российский сайт по поиску работы',
            'icon': 'hh-logo',
            'connection': hh_connection,
            'is_connected': hh_connection and hh_connection.is_active and hh_connection.is_token_valid(),
            'is_configured': hh_settings and bool(hh_settings.client_id),
            'connect_url': '/hh/connect',
            'disconnect_url': '/hh/disconnect'
        },
        'superjob': {
            'name': 'SuperJob',
            'description': 'Популярный российский сайт по поиску работы',
            'icon': 'superjob-logo',
            'connection': superjob_connection,
            'is_connected': superjob_connection and superjob_connection.is_active,
            'is_configured': superjob_settings and bool(superjob_settings.client_id),
            'connect_url': '/superjob/connect',
            'disconnect_url': '/superjob/disconnect'
        }
    }
    
    return render_template('integrations/platforms.html', platforms=platforms_data)


@bp.route('/status/<platform>')
@login_required
def status(platform):
    if platform not in ['hh', 'superjob']:
        return jsonify({'error': 'Unknown platform'}), 400
    
    connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform=platform
    ).first()
    
    if not connection:
        return jsonify({
            'connected': False,
            'message': 'Аккаунт не подключен'
        })
    
    is_valid = connection.is_token_valid() if hasattr(connection, 'is_token_valid') else True
    
    return jsonify({
        'connected': connection.is_active and is_valid,
        'is_active': connection.is_active,
        'token_valid': is_valid,
        'expires_at': connection.expires_at.isoformat() if connection.expires_at else None
    })


@bp.route('/publish/<int:resume_id>/<platform>', methods=['POST'])
@login_required
def publish_to_platform(resume_id, platform):
    if platform not in ['hh', 'superjob']:
        return jsonify({'error': 'Неизвестная платформа'}), 400
    
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    
    connection = PlatformConnection.query.filter_by(
        user_id=current_user.id,
        platform=platform
    ).first()
    
    if not connection or not connection.is_active:
        platform_name = 'HH.ru' if platform == 'hh' else 'SuperJob'
        return jsonify({'error': f'Сначала подключитесь к {platform_name}'}), 400
    
    if platform == 'hh':
        from app.services import hh_api
        
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
    
    elif platform == 'superjob':
        from app.services import superjob_service
        
        access_token = superjob_service.ensure_valid_token(connection)
        if not access_token:
            return jsonify({'error': 'Токен истек, переподключитесь к SuperJob'}), 401
        
        publication = ResumePublication(
            resume_id=resume.id,
            platform='superjob',
            status='processing'
        )
        db.session.add(publication)
        db.session.commit()
        
        try:
            adapted_data = superjob_service.adapt_resume_for_superjob(resume)
            
            if connection.external_resume_id:
                result = superjob_service.update_resume(access_token, connection.external_resume_id, adapted_data)
            else:
                result = superjob_service.create_resume(access_token, adapted_data)
            
            if result.get('success'):
                publication.status = 'published'
                publication.published_at = datetime.utcnow()
                if result.get('data'):
                    resume_id_sj = str(result['data'].get('id', ''))
                    publication.external_id = resume_id_sj
                    publication.external_url = f"https://www.superjob.ru/resume/{resume_id_sj}.html"
                    connection.external_resume_id = resume_id_sj
                    connection.external_resume_url = publication.external_url
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Резюме опубликовано на SuperJob!',
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
