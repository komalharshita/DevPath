from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from models import db, Project, User

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def check_admin():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    user = db.session.get(User, user_id)
    if not user or not user.is_admin:
        abort(403)

@admin_bp.route('/')
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Project.query.order_by(Project.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/dashboard.html', pagination=pagination)

def _get_list_from_form(field_name):
    # The form might send comma-separated strings or multiple values
    val = request.form.get(field_name, '')
    if not val:
        return []
    # Split by comma and strip whitespace
    return [item.strip() for item in val.split(',') if item.strip()]

@admin_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        project = Project(
            title=request.form.get('title', ''),
            level=request.form.get('level', ''),
            interest=request.form.get('interest', ''),
            time=request.form.get('time', ''),
            description=request.form.get('description', ''),
            skills=_get_list_from_form('skills'),
            features=_get_list_from_form('features'),
            tech_stack=_get_list_from_form('tech_stack'),
            roadmap=_get_list_from_form('roadmap'),
            resources=_get_list_from_form('resources'),
            starter_code=request.form.get('starter_code', '')
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/form.html', project=None)

@admin_bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = db.session.get(Project, id)
    if not project:
        abort(404)
        
    if request.method == 'POST':
        project.title = request.form.get('title', '')
        project.level = request.form.get('level', '')
        project.interest = request.form.get('interest', '')
        project.time = request.form.get('time', '')
        project.description = request.form.get('description', '')
        project.skills = _get_list_from_form('skills')
        project.features = _get_list_from_form('features')
        project.tech_stack = _get_list_from_form('tech_stack')
        project.roadmap = _get_list_from_form('roadmap')
        project.resources = _get_list_from_form('resources')
        project.starter_code = request.form.get('starter_code', '')
        
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/form.html', project=project)

@admin_bp.route('/projects/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = db.session.get(Project, id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for('admin.dashboard'))
