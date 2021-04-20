from flask import Blueprint, render_template

settings = Blueprint('settings', __name__)

@settings.route('/profile')
def profile():

      return render_template("client/profile.html", user=current_user)