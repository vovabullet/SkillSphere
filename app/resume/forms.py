from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Optional, Length

class ResumeBasicForm(FlaskForm):
    title = StringField('Название резюме', validators=[DataRequired(), Length(max=200)])
    template = SelectField('Шаблон', choices=[
        ('classic', 'Классический'),
        ('modern', 'Современный'),
        ('minimal', 'Минималистичный'),
        ('tech', 'Технический')
    ], validators=[DataRequired()])
    
    full_name = StringField('Полное имя', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Optional(), Length(max=50)])
    location = StringField('Местоположение', validators=[Optional(), Length(max=200)])
    summary = TextAreaField('О себе', validators=[Optional()])
    photo = FileField('Фотография', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')])

class EducationEntryForm(FlaskForm):
    institution = StringField('Учебное заведение', validators=[DataRequired()])
    degree = StringField('Степень/Специальность', validators=[DataRequired()])
    start_date = StringField('Дата начала', validators=[DataRequired()])
    end_date = StringField('Дата окончания', validators=[Optional()])
    description = TextAreaField('Описание', validators=[Optional()])

class ExperienceEntryForm(FlaskForm):
    company = StringField('Компания', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    start_date = StringField('Дата начала', validators=[DataRequired()])
    end_date = StringField('Дата окончания', validators=[Optional()])
    description = TextAreaField('Обязанности и достижения', validators=[Optional()])
