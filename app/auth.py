from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, oauth
from flask_login import login_user, login_required, logout_user, current_user
import os

auth = Blueprint('auth', __name__)

google = oauth.register(
    name = os.getenv("GOOGLE_NAME"),
    client_id = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
    client_kwargs={'scope': 'openid email profile'},
)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('mail.inbox'))
            else:
                flash('Incorrenct password', category='error')
        else:
            flash('Email does not exists password', category='error')

    return render_template("client/login.html", user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('User is already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 character', category='error')
        elif len(first_name) < 2:
            flash('Firstname must be greater than 2 character', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('Passwords must be atleast 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1),
                            issocialmedia=False)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account Created', category='success')
            return redirect(url_for('views.home'))

    return render_template("client/sign_up.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    for key in list(session.keys()):
        session.pop(key)
    return  render_template("client/login.html", user=current_user)


@auth.route('/google-login', methods=['POST'])
def google_login():
    if request.method == 'POST':
        google = oauth.create_client(os.getenv("GOOGLE_NAME"))  # create the google oauth client
        redirect_uri = url_for('auth.google_authenticate', _external=True)
        return google.authorize_redirect(redirect_uri)

@auth.route('/google_authenticate')
def google_authenticate():
    google = oauth.create_client(os.getenv("GOOGLE_NAME")) 
    token = google.authorize_access_token()
    resp = google.get('userinfo') 
    user_info = resp.json()

    email =  user_info['email']
    first_name = user_info['name'] + ' ' + user_info['family_name']
    l_user = User.query.filter_by(email=user_info['email']).first()

    if l_user:
        login_user(l_user, remember=True)
        flash('Login Successfuly', category='success')

        return redirect(url_for('mail.inbox', _external=True))
    else:
        new_user = User(email=email, first_name=first_name, is_social_media=True, media_type='google')
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('Account Created', category='success')
        flash('Login Successfuly', category='success')

        return redirect(url_for('mail.inbox', _external=True))
  
  