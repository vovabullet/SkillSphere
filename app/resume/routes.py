from flask import render_template, redirect, url_for, flash, request, make_response, jsonify
from flask_login import login_required, current_user
from app.resume import bp
from app.resume.forms import ResumeBasicForm
from app.models.resume import Resume
from app import db
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from app.services.gigachat_service import analyze_resume, improve_text, generate_summary, validate_job_title, generate_resume_data
from app.templates_config import get_all_templates, get_template

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(photo_file):
    if photo_file and allowed_file(photo_file.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(photo_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        photo_file.save(os.path.join(UPLOAD_FOLDER, filename))
        return filename
    return None

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ResumeBasicForm()
    if form.validate_on_submit():
        template = form.template.data or 'classic'
        
        photo_filename = None
        if form.photo.data:
            photo_filename = save_photo(form.photo.data)
        
        resume = Resume(
            title=form.title.data,
            template=template,
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            location=form.location.data,
            summary=form.summary.data,
            photo_path=photo_filename,
            user_id=current_user.id,
            is_draft=True
        )
        
        prefilled_skills = request.form.get('prefilled_skills')
        prefilled_experience = request.form.get('prefilled_experience')
        prefilled_education = request.form.get('prefilled_education')
        
        if prefilled_skills:
            try:
                resume.set_skills(json.loads(prefilled_skills))
            except:
                pass
        
        if prefilled_experience:
            try:
                resume.set_experience(json.loads(prefilled_experience))
            except:
                pass
        
        if prefilled_education:
            try:
                resume.set_education(json.loads(prefilled_education))
            except:
                pass
        
        db.session.add(resume)
        db.session.commit()
        flash('Резюме создано успешно!', 'success')
        return redirect(url_for('resume.edit', id=resume.id))
    
    return render_template('resume/create.html', title='Создать резюме', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        flash('У вас нет доступа к этому резюме.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('resume/edit.html', title='Редактировать резюме', resume=resume)

@bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    resume.title = data.get('title', resume.title)
    
    template = data.get('template', resume.template)
    if template in ['classic', 'modern', 'minimal', 'tech']:
        resume.template = template
    
    resume.full_name = data.get('full_name', resume.full_name)
    resume.email = data.get('email', resume.email)
    resume.phone = data.get('phone', resume.phone)
    resume.location = data.get('location', resume.location)
    resume.summary = data.get('summary', resume.summary)
    
    if 'education' in data:
        resume.set_education(data['education'])
    if 'experience' in data:
        resume.set_experience(data['experience'])
    if 'skills' in data:
        resume.set_skills(data['skills'])
    if 'portfolio' in data:
        resume.set_portfolio(data['portfolio'])
    
    resume.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Резюме обновлено'})

@bp.route('/upload-photo/<int:id>', methods=['POST'])
@login_required
def upload_photo(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'photo' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    photo_filename = save_photo(photo)
    if photo_filename:
        resume.photo_path = photo_filename
        db.session.commit()
        return jsonify({'success': True, 'photo_path': photo_filename, 'message': 'Фото загружено успешно'})
    else:
        return jsonify({'error': 'Недопустимый формат файла'}), 400

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(resume)
    db.session.commit()
    flash('Резюме удалено.', 'info')
    return redirect(url_for('main.dashboard'))

@bp.route('/preview/<int:id>')
@login_required
def preview(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        flash('У вас нет доступа к этому резюме.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    template_name = resume.template
    if template_name not in ['classic', 'modern', 'minimal', 'tech']:
        template_name = 'classic'
    
    return render_template(f'resume/templates/{template_name}.html', resume=resume)

@bp.route('/export/<int:id>')
@login_required
def export_pdf(id):
    from weasyprint import HTML
    from urllib.parse import quote
    
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        flash('У вас нет доступа к этому резюме.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    template_name = resume.template
    if template_name not in ['classic', 'modern', 'minimal', 'tech']:
        template_name = 'classic'
    
    html_content = render_template(f'resume/templates/{template_name}.html', resume=resume, for_pdf=True)
    
    base_url = request.host_url
    pdf = HTML(string=html_content, base_url=base_url).write_pdf()
    
    safe_filename = f"resume_{resume.id}.pdf"
    utf8_filename = f"resume_{resume.full_name.replace(' ', '_')}.pdf"
    encoded_filename = quote(utf8_filename.encode('utf-8'))
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"inline; filename=\"{safe_filename}\"; filename*=UTF-8''{encoded_filename}"
    
    return response

@bp.route('/publish/<int:id>', methods=['POST'])
@login_required
def publish(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    resume.is_draft = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Резюме опубликовано'})

@bp.route('/ai/analyze/<int:id>', methods=['POST'])
@login_required
def ai_analyze(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'У вас нет доступа к этому резюме'}), 403
    
    try:
        resume_text = resume.summary or ''
        
        experience_list = resume.get_experience()
        for exp in experience_list:
            if exp.get('description'):
                resume_text += '\n\n' + exp['description']
        
        if not resume_text.strip():
            return jsonify({'error': 'Резюме не содержит текста для анализа'}), 400
        
        recommendations = analyze_resume(resume_text)
        
        return jsonify({'success': True, 'data': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/improve', methods=['POST'])
@login_required
def ai_improve():
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Текст для улучшения не указан'}), 400
    
    text = data.get('text')
    job_title = data.get('job_title')
    
    try:
        improved_text = improve_text(text, job_title)
        
        return jsonify({'success': True, 'data': improved_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/generate-summary/<int:id>', methods=['POST'])
@login_required
def ai_generate_summary(id):
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'У вас нет доступа к этому резюме'}), 403
    
    data = request.json
    
    if not data or 'job_title' not in data:
        return jsonify({'error': 'Желаемая должность не указана'}), 400
    
    job_title = data.get('job_title')
    
    try:
        experience_list = resume.get_experience()
        experience_text = ''
        
        for exp in experience_list:
            position = exp.get('position', '').strip()
            company = exp.get('company', '').strip()
            description = exp.get('description', '').strip()
            
            if position or company or description:
                exp_entry = []
                if position:
                    exp_entry.append(f"Должность: {position}")
                if company:
                    exp_entry.append(f"Компания: {company}")
                if description:
                    exp_entry.append(f"Описание: {description}")
                experience_text += '\n'.join(exp_entry) + '\n\n'
        
        skills_list = resume.get_skills()
        if skills_list:
            skill_names = []
            for skill in skills_list:
                if isinstance(skill, dict):
                    skill_name = skill.get('name', '').strip()
                    if skill_name:
                        skill_names.append(skill_name)
                elif isinstance(skill, str) and skill.strip():
                    skill_names.append(skill.strip())
            
            if skill_names:
                experience_text += "Навыки: " + ', '.join(skill_names) + '\n'
        
        if not experience_text.strip():
            return jsonify({'error': 'Резюме не содержит опыта работы для генерации summary'}), 400
        
        summary_text = generate_summary(experience_text, job_title)
        
        return jsonify({'success': True, 'data': summary_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/templates', methods=['GET'])
@login_required
def get_templates():
    """Получить список всех доступных шаблонов"""
    templates = get_all_templates()
    return jsonify({'success': True, 'templates': templates})

@bp.route('/get-customization/<int:id>', methods=['GET'])
@login_required
def get_customization(id):
    """Получить кастомизацию резюме"""
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'У вас нет доступа к этому резюме'}), 403
    
    return jsonify({
        'success': True,
        'customization': resume.get_customization()
    })

@bp.route('/apply-template/<int:id>', methods=['POST'])
@login_required
def apply_template(id):
    """Применить шаблон к резюме"""
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'У вас нет доступа к этому резюме'}), 403
    
    data = request.json
    if not data or 'template_name' not in data:
        return jsonify({'error': 'Название шаблона не указано'}), 400
    
    template_name = data.get('template_name')
    template = get_template(template_name)
    
    resume.template = template_name
    resume.set_customization({
        'font': template['font'],
        'primary_color': template['primary_color'],
        'secondary_color': template['secondary_color'],
        'sections': template['sections']
    })
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Шаблон "{template["name"]}" применён успешно',
        'customization': resume.get_customization()
    })

@bp.route('/customize/<int:id>', methods=['POST'])
@login_required
def customize(id):
    """Сохранить кастомизацию резюме"""
    resume = Resume.query.get_or_404(id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'У вас нет доступа к этому резюме'}), 403
    
    data = request.json
    if not data:
        return jsonify({'error': 'Данные кастомизации не указаны'}), 400
    
    current_customization = resume.get_customization()
    
    if 'font' in data:
        current_customization['font'] = data['font']
    if 'primary_color' in data:
        current_customization['primary_color'] = data['primary_color']
    if 'secondary_color' in data:
        current_customization['secondary_color'] = data['secondary_color']
    if 'sections' in data:
        current_customization['sections'].update(data['sections'])
    
    resume.set_customization(current_customization)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Настройки сохранены',
        'customization': resume.get_customization()
    })


@bp.route('/ai-generate', methods=['POST'])
@login_required
def ai_generate():
    """Генерация данных резюме с помощью ИИ"""
    data = request.json
    if not data or not data.get('job_title'):
        return jsonify({'success': False, 'error': 'Укажите название должности'}), 400
    
    job_title = data['job_title'].strip()
    
    validation = validate_job_title(job_title)
    
    if not validation.get('valid', True):
        return jsonify({
            'success': False,
            'error': validation.get('message', 'Это не похоже на реальную должность. Пожалуйста, введите корректное название.')
        }), 400
    
    try:
        resume_data = generate_resume_data(validation.get('normalized_title', job_title))
        
        skills_formatted = [{'name': skill, 'level': 80} for skill in resume_data.get('skills', [])]
        
        return jsonify({
            'success': True,
            'data': {
                'title': resume_data.get('title', job_title),
                'summary': resume_data.get('summary', ''),
                'skills': skills_formatted
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка генерации: {str(e)}'
        }), 500
