from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from backend.models import db, Resume, JobDescription
from training.nlp_engine import nlp_engine, NLPEngine
from werkzeug.utils import secure_filename
import os
from pdfminer.high_level import extract_text

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('index.html')

@routes.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access Denied: Admin only', 'danger')
        return redirect(url_for('routes.user_dashboard'))
    
    # Check if we have resumes, if using a join might be better, but relationships handle it
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
    jds = JobDescription.query.all()
    
    return render_template('admin_dashboard.html', resumes=resumes, jds=jds)

@routes.route('/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash('Access Denied: User only', 'warning')
        return redirect(url_for('routes.admin_dashboard'))
    
    jds = JobDescription.query.all()
    # Filter my resumes (applications)
    my_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    
    return render_template('user_dashboard.html', jobs=jds, applications=my_resumes)

@routes.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part', 'danger')

        return redirect(url_for('routes.user_dashboard'))
        
    file = request.files['resume']
    job_id = request.form.get('job_id')
    jd_text = request.form.get('jd_text')
    
    if not job_id and not jd_text:
        flash('Please select a job OR enter a job description', 'warning')
        return redirect(url_for('routes.user_dashboard'))

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('routes.user_dashboard'))
        
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            # 1. Extract Text
            text = extract_text(filepath)
            
            # 2. Fetch Job Description
            jd_description = ""
            if job_id:
                jd = JobDescription.query.get(job_id)
                if not jd:
                    flash('Job not found', 'danger')
                    return redirect(url_for('routes.user_dashboard'))
                jd_description = jd.description
            elif jd_text:
                jd_description = jd_text
                # For DB integrity, we might need a dummy Job or allow NULL job_id. 
                # But schema says job_id is NOT NULL.
                # So we must creating a temporary or "User Provided" job?
                # Or we change schema to allow NULL job_id?
                # Steps said: "Either Add missing job_id column...". 
                # Let's create a dynamic JobDescription for this user or find a "Self" job.
                # BETTER: Create a new JobDescription for this submission automatically.
                new_jd = JobDescription(title=f"Custom Job - {current_user.username}", description=jd_text)
                db.session.add(new_jd)
                db.session.flush() # get ID
                job_id = new_jd.id
                jd_description = new_jd.description
            
            # 3. Calculate Score Immediately
            score = nlp_engine.calculate_score(text, jd_description)
            
            # 4. Determine Status
            status = 'Pending'
            if score >= 70:
                status = 'Shortlisted'
            elif score < 30:
                status = 'Rejected'
            
            # 5. Save Application (Resume linked to Job)
            new_resume = Resume(
                user_id=current_user.id,
                job_id=job_id,
                filename=filename,
                content=text,
                score=score,
                status=status
            )
            db.session.add(new_resume)
            db.session.commit()
            
            flash(f'Application submitted! Match Score: {score}%. Status: {status}', 'success')
        except Exception as e:
            flash(f'Error processing application: {str(e)}', 'danger')
            
    else:
        flash('Only PDF files are allowed', 'danger')
        
    return redirect(url_for('routes.user_dashboard'))

@routes.route('/update_status/<int:resume_id>', methods=['POST'])
@login_required
def update_status(resume_id):
    if current_user.role != 'admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('routes.user_dashboard'))
        
    resume = Resume.query.get_or_404(resume_id)
    new_status = request.form.get('status')
    
    if new_status:
        resume.status = new_status
        db.session.commit()
        flash(f'Status updated to {new_status}', 'success')
        
    return redirect(url_for('routes.admin_dashboard'))

@routes.route('/add_jd', methods=['POST'])
@login_required
def add_jd():
    if current_user.role != 'admin':
        return redirect(url_for('routes.user_dashboard'))
        
    title = request.form.get('title')
    description = request.form.get('description')
    
    new_jd = JobDescription(title=title, description=description)
    db.session.add(new_jd)
    db.session.commit()
    flash('Job Description added!', 'success')
    return redirect(url_for('routes.admin_dashboard'))
