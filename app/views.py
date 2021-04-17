from flask import Blueprint, render_template, request, session
from flask_login import login_user, login_required, logout_user, current_user


views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
     return render_template("client/home.html", user=current_user)


@views.route('/settings/profile')
@login_required
def profile():
     return render_template("client/profile.html", user=current_user)