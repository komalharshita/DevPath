from flask import Blueprint, session, redirect, url_for, current_app
from models import db, User

# We import github from app, but since it's instantiated there, it might cause circular import.
# Instead, we can import it locally or place the blueprint accordingly.
# A better way is to pass github from app, or just import it.
# To avoid circular imports, let's delay import or import github from the current_app context or from a dedicated module.
# For simplicity, we can do from app import github

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    from app import github
    # generate a redirect uri
    redirect_uri = url_for('auth.authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    from app import github
    token = github.authorize_access_token()
    if not token:
        return redirect(url_for('main.index'))
    
    resp = github.get('user', token=token)
    profile = resp.json()
    
    github_id = str(profile.get('id'))
    username = profile.get('login')
    avatar_url = profile.get('avatar_url')
    
    if not github_id:
        return redirect(url_for('main.index'))
        
    user = User.query.filter_by(github_id=github_id).first()
    if not user:
        user = User(
            github_id=github_id,
            username=username,
            avatar_url=avatar_url
        )
        db.session.add(user)
    else:
        user.username = username
        user.avatar_url = avatar_url
        
    db.session.commit()
    
    session['user_id'] = user.id
    return redirect(url_for('main.profile'))

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))
