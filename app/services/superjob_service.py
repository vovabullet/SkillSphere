import requests
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode

SJ_AUTH_URL = 'https://www.superjob.ru/authorize/'
SJ_TOKEN_URL = 'https://api.superjob.ru/2.0/oauth2/access_token/'
SJ_API_URL = 'https://api.superjob.ru/2.0'


def _get_credentials():
    from app.models.api_settings import ApiSettings
    settings = ApiSettings.get_settings('superjob')
    if settings and settings.client_id:
        return {
            'client_id': settings.client_id,
            'client_secret': settings.client_secret,
            'redirect_uri': settings.redirect_uri
        }
    return {
        'client_id': os.environ.get('SUPERJOB_CLIENT_ID', ''),
        'client_secret': os.environ.get('SUPERJOB_CLIENT_SECRET', ''),
        'redirect_uri': os.environ.get('SUPERJOB_REDIRECT_URI', '')
    }


def get_auth_url(state=None):
    creds = _get_credentials()
    params = {
        'client_id': creds['client_id'],
        'redirect_uri': creds['redirect_uri'],
        'response_type': 'code',
    }
    if state:
        params['state'] = state
    return f"{SJ_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    creds = _get_credentials()
    data = {
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'code': code,
        'redirect_uri': creds['redirect_uri'],
        'grant_type': 'authorization_code',
    }
    
    try:
        response = requests.post(SJ_TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('ttl', 3600))
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': expires_at
            }
        else:
            print(f"SuperJob token exchange error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"SuperJob token exchange exception: {e}")
    return None


def refresh_access_token(refresh_token):
    creds = _get_credentials()
    data = {
        'refresh_token': refresh_token,
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'grant_type': 'refresh_token',
    }
    
    try:
        response = requests.post(SJ_TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('ttl', 3600))
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': expires_at
            }
        else:
            print(f"SuperJob token refresh error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"SuperJob token refresh exception: {e}")
    return None


def ensure_valid_token(connection):
    from app import db
    
    if connection.is_token_valid():
        return connection.access_token
    
    if connection.refresh_token:
        token_data = refresh_access_token(connection.refresh_token)
        if token_data:
            connection.access_token = token_data['access_token']
            connection.refresh_token = token_data['refresh_token']
            connection.expires_at = token_data['expires_at']
            db.session.commit()
            return connection.access_token
    
    return None


def get_user_info(access_token):
    creds = _get_credentials()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Api-App-Id': creds['client_secret']
    }
    try:
        response = requests.get(f'{SJ_API_URL}/user/current/', headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"SuperJob get_user_info error: {e}")
    return None


def get_user_resumes(access_token):
    creds = _get_credentials()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Api-App-Id': creds['client_secret']
    }
    try:
        response = requests.get(f'{SJ_API_URL}/user/resumes/', headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"SuperJob get_user_resumes error: {e}")
    return None


def create_resume(access_token, resume_data):
    creds = _get_credentials()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Api-App-Id': creds['client_secret'],
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{SJ_API_URL}/user/resumes/',
            headers=headers,
            json=resume_data
        )
        
        if response.status_code in [200, 201]:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.text, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def update_resume(access_token, resume_id, resume_data):
    creds = _get_credentials()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Api-App-Id': creds['client_secret'],
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.put(
            f'{SJ_API_URL}/user/resumes/{resume_id}/',
            headers=headers,
            json=resume_data
        )
        
        if response.status_code in [200, 204]:
            return {'success': True}
        else:
            return {'success': False, 'error': response.text, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def adapt_resume_for_superjob(resume):
    name_parts = (resume.full_name or '').split()
    first_name = name_parts[0] if name_parts else 'Имя'
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Фамилия'
    
    sj_resume = {
        'profession': resume.title or 'Специалист',
        'firstname': first_name,
        'lastname': last_name,
        'phone': resume.phone or '',
        'email': resume.email or '',
        'town': {'id': 4},
        'gender': 1,
        'type_of_work': 6,
        'place_of_work': 0,
        'education': 4,
        'experience': [],
    }
    
    experience = resume.get_experience()
    for exp in experience:
        sj_exp = {
            'name': exp.get('company', 'Компания'),
            'profession': exp.get('position', 'Специалист'),
            'work': exp.get('description', ''),
        }
        
        if exp.get('start_date'):
            try:
                start_parts = exp['start_date'].split('-')
                if len(start_parts) >= 2:
                    sj_exp['date_start'] = f"{start_parts[0]}-{start_parts[1]}"
            except:
                pass
        
        if exp.get('end_date'):
            try:
                end_parts = exp['end_date'].split('-')
                if len(end_parts) >= 2:
                    sj_exp['date_end'] = f"{end_parts[0]}-{end_parts[1]}"
            except:
                pass
        
        sj_resume['experience'].append(sj_exp)
    
    skills = resume.get_skills()
    if skills:
        skill_names = []
        for skill in skills:
            if isinstance(skill, dict) and skill.get('name'):
                skill_names.append(skill['name'])
            elif isinstance(skill, str):
                skill_names.append(skill)
        if skill_names:
            sj_resume['skills'] = ', '.join(skill_names)
    
    education_list = resume.get_education()
    if education_list:
        sj_resume['education_history'] = []
        for edu in education_list:
            sj_edu = {
                'name': edu.get('institution', 'Университет'),
                'faculty': edu.get('degree', 'Специальность'),
            }
            if edu.get('end_date'):
                try:
                    sj_edu['year_end'] = int(edu['end_date'].split('-')[0])
                except:
                    pass
            sj_resume['education_history'].append(sj_edu)
    
    if resume.summary:
        sj_resume['additional'] = resume.summary
    
    return sj_resume
