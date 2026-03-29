import requests
import os
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode
import base64

from app.services.encryption_service import encrypt_token, decrypt_token

HH_AUTH_URL = 'https://hh.ru/oauth/authorize'
HH_TOKEN_URL = 'https://hh.ru/oauth/token'
HH_API_URL = 'https://api.hh.ru'


def _get_credentials():
    from app.models.api_settings import ApiSettings
    settings = ApiSettings.get_settings('hh')
    if settings and settings.client_id:
        return {
            'client_id': settings.client_id,
            'client_secret': settings.client_secret,
            'redirect_uri': settings.redirect_uri
        }
    return {
        'client_id': os.environ.get('HH_CLIENT_ID', ''),
        'client_secret': os.environ.get('HH_CLIENT_SECRET', ''),
        'redirect_uri': os.environ.get('HH_REDIRECT_URI', '')
    }


def generate_state():
    return secrets.token_urlsafe(32)


def get_auth_url(state):
    creds = _get_credentials()
    params = {
        'response_type': 'code',
        'client_id': creds['client_id'],
        'redirect_uri': creds['redirect_uri'],
        'state': state
    }
    return f"{HH_AUTH_URL}?{urlencode(params)}"


def _get_basic_auth_header():
    creds = _get_credentials()
    credentials = f"{creds['client_id']}:{creds['client_secret']}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def exchange_code_for_token(code):
    creds = _get_credentials()
    headers = {
        'Authorization': _get_basic_auth_header(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': creds['redirect_uri'],
    }
    
    try:
        response = requests.post(HH_TOKEN_URL, data=data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': expires_at
            }
        else:
            print(f"HH token exchange error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"HH token exchange exception: {e}")
    return None


def refresh_access_token(encrypted_refresh_token):
    refresh_token = decrypt_token(encrypted_refresh_token)
    if not refresh_token:
        return None
        
    headers = {
        'Authorization': _get_basic_auth_header(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    
    try:
        response = requests.post(HH_TOKEN_URL, data=data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
            
            new_refresh_token = token_data.get('refresh_token')
            if new_refresh_token:
                encrypted_new_refresh = encrypt_token(new_refresh_token)
            else:
                encrypted_new_refresh = encrypted_refresh_token
            
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': encrypted_new_refresh,
                'expires_at': expires_at
            }
        else:
            print(f"HH token refresh error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"HH token refresh exception: {e}")
    return None


def ensure_valid_token(connection):
    from app import db
    
    if connection.is_token_valid():
        return connection.access_token
    
    if connection.refresh_token_encrypted:
        token_data = refresh_access_token(connection.refresh_token_encrypted)
        if token_data:
            connection.access_token = token_data['access_token']
            connection.refresh_token_encrypted = token_data['refresh_token']
            connection.expires_at = token_data['expires_at']
            db.session.commit()
            return connection.access_token
    
    return None


def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(f'{HH_API_URL}/me', headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"HH get_user_info error: {e}")
    return None


def get_user_resumes(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(f'{HH_API_URL}/resumes/mine', headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"HH get_user_resumes error: {e}")
    return None


def create_resume(access_token, resume_data):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{HH_API_URL}/resumes',
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
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.put(
            f'{HH_API_URL}/resumes/{resume_id}',
            headers=headers,
            json=resume_data
        )
        
        if response.status_code in [200, 204]:
            return {'success': True}
        else:
            return {'success': False, 'error': response.text, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def publish_resume(access_token, resume_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.post(
            f'{HH_API_URL}/resumes/{resume_id}/publish',
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            return {'success': True}
        else:
            return {'success': False, 'error': response.text, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def adapt_resume_for_hh(resume):
    name_parts = (resume.full_name or '').split()
    first_name = name_parts[0] if name_parts else 'Имя'
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Фамилия'
    
    hh_resume = {
        'title': resume.title or 'Специалист',
        'first_name': first_name,
        'last_name': last_name,
        'area': {'id': '1'},
        'contact': [],
        'skill_set': [],
        'experience': [],
        'salary': {
            'amount': None,
            'currency': 'RUR'
        },
        'employment': {'id': 'full'},
        'schedule': {'id': 'fullDay'},
        'business_trip_readiness': {'id': 'ready'},
        'relocation': {
            'type': {'id': 'no_relocation'}
        }
    }
    
    if resume.email:
        hh_resume['contact'].append({
            'type': {'id': 'email'},
            'value': resume.email,
            'preferred': True
        })
    
    if resume.phone:
        phone_clean = ''.join(filter(str.isdigit, resume.phone))
        if len(phone_clean) >= 10:
            hh_resume['contact'].append({
                'type': {'id': 'cell'},
                'value': {
                    'country': '7',
                    'city': phone_clean[1:4] if len(phone_clean) > 4 else '',
                    'number': phone_clean[4:] if len(phone_clean) > 4 else phone_clean
                }
            })
    
    skills = resume.get_skills()
    if skills:
        for skill in skills:
            if isinstance(skill, dict) and skill.get('name'):
                hh_resume['skill_set'].append(skill['name'])
            elif isinstance(skill, str):
                hh_resume['skill_set'].append(skill)
    
    experience = resume.get_experience()
    for exp in experience:
        hh_exp = {
            'company': exp.get('company', 'Компания'),
            'company_url': None,
            'position': exp.get('position', 'Специалист'),
            'description': exp.get('description', ''),
        }
        
        if exp.get('start_date'):
            start_parts = exp['start_date'].split('-')
            if len(start_parts) >= 2:
                hh_exp['start'] = f"{start_parts[0]}-{start_parts[1]}-01"
        
        if exp.get('end_date'):
            end_parts = exp['end_date'].split('-')
            if len(end_parts) >= 2:
                hh_exp['end'] = f"{end_parts[0]}-{end_parts[1]}-01"
        
        hh_resume['experience'].append(hh_exp)
    
    education = resume.get_education()
    if education:
        hh_resume['education'] = {
            'level': {'id': 'higher'},
            'primary': []
        }
        for edu in education:
            hh_edu = {
                'name': edu.get('institution', 'Университет'),
                'organization': edu.get('institution', 'Университет'),
                'result': edu.get('degree', 'Специальность'),
                'year': None
            }
            if edu.get('end_date'):
                try:
                    hh_edu['year'] = int(edu['end_date'].split('-')[0])
                except:
                    pass
            hh_resume['education']['primary'].append(hh_edu)
    
    return hh_resume
