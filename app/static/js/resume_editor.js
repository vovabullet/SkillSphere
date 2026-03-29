let education = [];
let experience = [];
let skills = [];
let portfolio = [];

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function loadEducation() {
    education = resumeData.education || [];
    renderEducation();
}

function loadExperience() {
    experience = resumeData.experience || [];
    renderExperience();
}

function loadSkills() {
    skills = resumeData.skills || [];
    renderSkills();
}

function loadPortfolio() {
    portfolio = resumeData.portfolio || [];
    renderPortfolio();
}

function renderEducation() {
    const container = document.getElementById('education-list');
    container.innerHTML = '';
    
    education.forEach((edu, index) => {
        container.innerHTML += `
            <div class="entry-item mb-3">
                <button type="button" class="btn btn-sm btn-danger btn-remove" onclick="removeEducation(${index})">×</button>
                <div class="mb-2">
                    <input type="text" class="form-control mb-2" placeholder="Учебное заведение" 
                           value="${edu.institution || ''}" onchange="updateEducation(${index}, 'institution', this.value)">
                    <input type="text" class="form-control mb-2" placeholder="Степень/Специальность" 
                           value="${edu.degree || ''}" onchange="updateEducation(${index}, 'degree', this.value)">
                    <div class="row">
                        <div class="col-6">
                            <input type="text" class="form-control mb-2" placeholder="Дата начала" 
                                   value="${edu.start_date || ''}" onchange="updateEducation(${index}, 'start_date', this.value)">
                        </div>
                        <div class="col-6">
                            <input type="text" class="form-control mb-2" placeholder="Дата окончания" 
                                   value="${edu.end_date || ''}" onchange="updateEducation(${index}, 'end_date', this.value)">
                        </div>
                    </div>
                    <textarea class="form-control" placeholder="Описание" rows="2" 
                              onchange="updateEducation(${index}, 'description', this.value)">${edu.description || ''}</textarea>
                </div>
            </div>
        `;
    });
}

function renderExperience() {
    const container = document.getElementById('experience-list');
    container.innerHTML = '';
    
    experience.forEach((exp, index) => {
        container.innerHTML += `
            <div class="entry-item mb-3">
                <button type="button" class="btn btn-sm btn-danger btn-remove" onclick="removeExperience(${index})">×</button>
                <div class="mb-2">
                    <input type="text" class="form-control mb-2" placeholder="Компания" 
                           value="${exp.company || ''}" onchange="updateExperience(${index}, 'company', this.value)">
                    <input type="text" class="form-control mb-2" placeholder="Должность" 
                           value="${exp.position || ''}" onchange="updateExperience(${index}, 'position', this.value)">
                    <div class="row">
                        <div class="col-6">
                            <input type="text" class="form-control mb-2" placeholder="Дата начала" 
                                   value="${exp.start_date || ''}" onchange="updateExperience(${index}, 'start_date', this.value)">
                        </div>
                        <div class="col-6">
                            <input type="text" class="form-control mb-2" placeholder="Дата окончания" 
                                   value="${exp.end_date || ''}" onchange="updateExperience(${index}, 'end_date', this.value)">
                        </div>
                    </div>
                    <textarea class="form-control" placeholder="Обязанности и достижения" rows="3" 
                              onchange="updateExperience(${index}, 'description', this.value)">${exp.description || ''}</textarea>
                </div>
            </div>
        `;
    });
}

function renderSkills() {
    const container = document.getElementById('skills-list');
    container.innerHTML = '';
    
    skills.forEach((skill, index) => {
        container.innerHTML += `
            <div class="entry-item mb-2" style="display: flex; align-items: center;">
                <input type="text" class="form-control" placeholder="Навык" 
                       value="${skill.name || ''}" onchange="updateSkill(${index}, 'name', this.value)">
                <button type="button" class="btn btn-sm btn-danger ms-2" onclick="removeSkill(${index})">×</button>
            </div>
        `;
    });
}

function renderPortfolio() {
    const container = document.getElementById('portfolio-list');
    if (!container) return;
    container.innerHTML = '';
    
    portfolio.forEach((item, index) => {
        container.innerHTML += `
            <div class="entry-item mb-3 p-3 border rounded">
                <button type="button" class="btn btn-sm btn-danger btn-remove" onclick="removePortfolioItem(${index})">×</button>
                <div class="mb-2">
                    <input type="text" class="form-control mb-2" placeholder="Название проекта/работы" 
                           value="${item.title || ''}" onchange="updatePortfolio(${index}, 'title', this.value)">
                    <input type="url" class="form-control mb-2" placeholder="Ссылка на проект (необязательно)" 
                           value="${item.url || ''}" onchange="updatePortfolio(${index}, 'url', this.value)">
                    <textarea class="form-control mb-2" placeholder="Описание проекта, ваша роль, технологии" rows="3" 
                              onchange="updatePortfolio(${index}, 'description', this.value)">${item.description || ''}</textarea>
                    <input type="text" class="form-control" placeholder="Технологии (через запятую)" 
                           value="${item.technologies || ''}" onchange="updatePortfolio(${index}, 'technologies', this.value)">
                </div>
            </div>
        `;
    });
}

function addEducation() {
    education.push({});
    renderEducation();
}

function addExperience() {
    experience.push({});
    renderExperience();
}

function addSkill() {
    skills.push({});
    renderSkills();
}

function addPortfolioItem() {
    portfolio.push({});
    renderPortfolio();
}

function updateEducation(index, field, value) {
    education[index][field] = value;
}

function updateExperience(index, field, value) {
    experience[index][field] = value;
}

function updateSkill(index, field, value) {
    skills[index][field] = value;
}

function updatePortfolio(index, field, value) {
    portfolio[index][field] = value;
}

function removeEducation(index) {
    education.splice(index, 1);
    renderEducation();
}

function removeExperience(index) {
    experience.splice(index, 1);
    renderExperience();
}

function removeSkill(index) {
    skills.splice(index, 1);
    renderSkills();
}

function removePortfolioItem(index) {
    portfolio.splice(index, 1);
    renderPortfolio();
}

function saveResume() {
    const data = {
        title: document.getElementById('title').value,
        template: document.getElementById('template').value,
        full_name: document.getElementById('full_name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        location: document.getElementById('location').value,
        summary: document.getElementById('summary').value,
        education: education,
        experience: experience,
        skills: skills,
        portfolio: portfolio
    };
    
    fetch(`/resume/update/${resumeData.id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Резюме успешно сохранено!');
        } else {
            alert('Ошибка при сохранении');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при сохранении');
    });
}

function publishResume() {
    if (confirm('Вы уверены, что хотите опубликовать это резюме?')) {
        fetch(`/resume/publish/${resumeData.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Резюме опубликовано!');
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function analyzeResume() {
    showAILoading();
    
    fetch(`/resume/ai/analyze/${resumeData.id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка сервера');
            }).catch(e => {
                if (e.message.includes('JSON')) {
                    throw new Error('Ошибка сервера. Попробуйте позже.');
                }
                throw e;
            });
        }
        return response.json();
    })
    .then(data => {
        hideAILoading();
        if (data.success) {
            showAIResult(data.data, 'Рекомендации по улучшению резюме');
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        hideAILoading();
        alert('Ошибка при анализе: ' + error.message);
    });
}

function generateSummary() {
    const jobTitle = prompt('Введите желаемую должность:');
    if (!jobTitle) return;
    
    showAILoading();
    
    fetch(`/resume/ai/generate-summary/${resumeData.id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ job_title: jobTitle })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка сервера');
            }).catch(e => {
                if (e.message.includes('JSON')) {
                    throw new Error('Ошибка сервера. Попробуйте позже.');
                }
                throw e;
            });
        }
        return response.json();
    })
    .then(data => {
        hideAILoading();
        if (data.success) {
            document.getElementById('summary').value = data.data;
            showAIResult('Summary успешно сгенерирован и добавлен в поле "О себе"', 'Успех');
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        hideAILoading();
        alert('Ошибка при генерации: ' + error.message);
    });
}

function showImproveTextModal() {
    const modal = new bootstrap.Modal(document.getElementById('improveTextModal'));
    modal.show();
}

function improveText() {
    const text = document.getElementById('textToImprove').value;
    const jobTitle = document.getElementById('jobTitleForImprove').value;
    
    if (!text) {
        alert('Введите текст для улучшения');
        return;
    }
    
    showAILoading();
    const modal = bootstrap.Modal.getInstance(document.getElementById('improveTextModal'));
    modal.hide();
    
    fetch('/resume/ai/improve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ 
            text: text,
            job_title: jobTitle || null
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка сервера');
            }).catch(e => {
                if (e.message.includes('JSON')) {
                    throw new Error('Ошибка сервера. Попробуйте позже.');
                }
                throw e;
            });
        }
        return response.json();
    })
    .then(data => {
        hideAILoading();
        if (data.success) {
            showAIResult(data.data, 'Улучшенный текст');
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        hideAILoading();
        alert('Ошибка при улучшении: ' + error.message);
    });
}

function showAILoading() {
    document.getElementById('ai-loading').style.display = 'block';
    document.getElementById('ai-result').style.display = 'none';
}

function hideAILoading() {
    document.getElementById('ai-loading').style.display = 'none';
}

function showAIResult(content, title) {
    const resultDiv = document.getElementById('ai-result-content');
    if (title) {
        resultDiv.innerHTML = `<strong>${title}:</strong><br><br>${content.replace(/\n/g, '<br>')}`;
    } else {
        resultDiv.innerHTML = content.replace(/\n/g, '<br>');
    }
    document.getElementById('ai-result').style.display = 'block';
}

function loadTemplates() {
    const grid = document.getElementById('templates-grid');
    if (!grid) {
        return;
    }
    
    fetch('/resume/templates')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderTemplates(data.templates);
            }
        })
        .catch(error => console.error('Error loading templates:', error));
}

function renderTemplates(templates) {
    const grid = document.getElementById('templates-grid');
    if (!grid) {
        return;
    }
    grid.innerHTML = '';
    
    for (const [key, template] of Object.entries(templates)) {
        const col = document.createElement('div');
        col.className = 'col';
        col.innerHTML = `
            <div class="card h-100 template-card" style="cursor: pointer; border: 2px solid ${template.primary_color};">
                <div class="card-body">
                    <h6 class="card-title" style="color: ${template.primary_color};">${template.name}</h6>
                    <p class="card-text text-muted small">${template.description}</p>
                    <div class="d-flex gap-2 align-items-center mt-2">
                        <span class="badge" style="background: ${template.primary_color};">Цвет 1</span>
                        <span class="badge" style="background: ${template.secondary_color};">Цвет 2</span>
                    </div>
                    <button class="btn btn-sm btn-primary mt-3 w-100" onclick="applyTemplate('${key}')">
                        Применить
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(col);
    }
}

function applyTemplate(templateName) {
    if (!confirm('Применить этот шаблон? Текущие настройки дизайна будут заменены.')) {
        return;
    }
    
    fetch(`/resume/apply-template/${resumeData.id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ template_name: templateName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            loadCustomization(data.customization);
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при применении шаблона');
    });
}

function loadCustomization(customization) {
    if (!customization) {
        if (typeof resumeData === 'undefined' || !resumeData || !resumeData.id) {
            return;
        }
        fetch(`/resume/get-customization/${resumeData.id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadCustomization(data.customization);
                }
            })
            .catch(error => console.error('Error loading customization:', error));
        return;
    }
    
    const fontEl = document.getElementById('custom-font');
    const primaryColorEl = document.getElementById('custom-primary-color');
    const secondaryColorEl = document.getElementById('custom-secondary-color');
    
    if (fontEl) fontEl.value = customization.font || 'Arial';
    if (primaryColorEl) primaryColorEl.value = customization.primary_color || '#667eea';
    if (secondaryColorEl) secondaryColorEl.value = customization.secondary_color || '#764ba2';
    
    const sections = customization.sections || {};
    const summaryEl = document.getElementById('section-summary');
    const experienceEl = document.getElementById('section-experience');
    const educationEl = document.getElementById('section-education');
    const skillsEl = document.getElementById('section-skills');
    
    if (summaryEl) summaryEl.checked = sections.summary !== false;
    if (experienceEl) experienceEl.checked = sections.experience !== false;
    if (educationEl) educationEl.checked = sections.education !== false;
    if (skillsEl) skillsEl.checked = sections.skills !== false;
}

function updateCustomization() {
    const fontEl = document.getElementById('custom-font');
    const primaryColorEl = document.getElementById('custom-primary-color');
    const secondaryColorEl = document.getElementById('custom-secondary-color');
    const summaryEl = document.getElementById('section-summary');
    const experienceEl = document.getElementById('section-experience');
    const educationEl = document.getElementById('section-education');
    const skillsEl = document.getElementById('section-skills');
    
    if (!fontEl || !primaryColorEl || !secondaryColorEl) {
        return;
    }
    
    const customization = {
        font: fontEl.value,
        primary_color: primaryColorEl.value,
        secondary_color: secondaryColorEl.value,
        sections: {
            summary: summaryEl ? summaryEl.checked : true,
            experience: experienceEl ? experienceEl.checked : true,
            education: educationEl ? educationEl.checked : true,
            skills: skillsEl ? skillsEl.checked : true
        }
    };
    
    if (typeof resumeData === 'undefined' || !resumeData || !resumeData.id) {
        return;
    }
    
    fetch(`/resume/customize/${resumeData.id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(customization)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Customization saved');
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function uploadPhoto() {
    const photoInput = document.getElementById('photo');
    const file = photoInput.files[0];
    
    if (!file) {
        alert('Пожалуйста, выберите файл');
        return;
    }
    
    const formData = new FormData();
    formData.append('photo', file);
    
    fetch(`/resume/upload-photo/${resumeData.id}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Фото загружено успешно!');
            location.reload();
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при загрузке фото');
    });
}

function downloadPDF() {
    const link = document.createElement('a');
    link.href = `/resume/export/${resumeData.id}`;
    link.download = `resume_${resumeData.id}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function exportToHH() {
    fetch('/integrations/status/hh')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                autoPublishToHH();
            } else {
                if (confirm('Для публикации на HH.ru нужно подключить аккаунт. Перейти к подключению?')) {
                    window.location.href = '/integrations/platforms';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            downloadPDF();
            setTimeout(() => {
                window.open('https://hh.ru/applicant/resumes/new', '_blank');
            }, 500);
        });
}

function exportToSuperJob() {
    fetch('/integrations/status/superjob')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                autoPublishToSuperJob();
            } else {
                if (confirm('Для публикации на SuperJob нужно подключить аккаунт. Перейти к подключению?')) {
                    window.location.href = '/integrations/platforms';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            downloadPDF();
            setTimeout(() => {
                window.open('https://www.superjob.ru/resume/create/', '_blank');
            }, 500);
        });
}

function exportToLinkedIn() {
    downloadPDF();
    setTimeout(() => {
        window.open('https://www.linkedin.com/in/edit/new-resume/', '_blank');
    }, 500);
}

function showPublishStatus(text) {
    document.getElementById('publish-status').style.display = 'block';
    document.getElementById('publish-status-text').textContent = text;
    document.getElementById('publish-result').style.display = 'none';
}

function hidePublishStatus() {
    document.getElementById('publish-status').style.display = 'none';
}

function showPublishResult(message, isSuccess) {
    const resultDiv = document.getElementById('publish-result');
    resultDiv.className = isSuccess ? 'alert alert-success mb-3' : 'alert alert-danger mb-3';
    resultDiv.innerHTML = message;
    resultDiv.style.display = 'block';
}

function autoPublishToHH() {
    if (!confirm('Опубликовать резюме на HH.ru?')) return;
    
    showPublishStatus('Публикация на HH.ru...');
    
    fetch(`/integrations/publish/${resumeData.id}/hh`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        hidePublishStatus();
        if (data.success) {
            let message = 'Резюме успешно опубликовано на HH.ru!';
            if (data.url) {
                message += ` <a href="${data.url}" target="_blank" class="alert-link">Открыть резюме</a>`;
            }
            showPublishResult(message, true);
        } else {
            showPublishResult('Ошибка: ' + (data.error || 'Неизвестная ошибка'), false);
        }
    })
    .catch(error => {
        hidePublishStatus();
        showPublishResult('Ошибка подключения: ' + error, false);
    });
}

function autoPublishToSuperJob() {
    if (!confirm('Опубликовать резюме на SuperJob?')) return;
    
    showPublishStatus('Публикация на SuperJob...');
    
    fetch(`/integrations/publish/${resumeData.id}/superjob`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        hidePublishStatus();
        if (data.success) {
            let message = 'Резюме успешно опубликовано на SuperJob!';
            if (data.url) {
                message += ` <a href="${data.url}" target="_blank" class="alert-link">Открыть резюме</a>`;
            }
            showPublishResult(message, true);
        } else {
            showPublishResult('Ошибка: ' + (data.error || 'Неизвестная ошибка'), false);
        }
    })
    .catch(error => {
        hidePublishStatus();
        showPublishResult('Ошибка подключения: ' + error, false);
    });
}

function loadPublicationHistory() {
    fetch(`/integrations/publications/${resumeData.id}`)
        .then(response => response.json())
        .then(data => {
            if (data.publications && data.publications.length > 0) {
                console.log('Publication history:', data.publications);
            }
        })
        .catch(error => console.error('Error loading publications:', error));
}

window.addEventListener('DOMContentLoaded', function() {
    loadTemplates();
    const customization = typeof resumeCustomization !== 'undefined' ? resumeCustomization : null;
    if (customization) {
        loadCustomization(customization);
    }
    
    const photoInput = document.getElementById('photo');
    if (photoInput) {
        photoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                uploadPhoto();
            }
        });
    }
});
