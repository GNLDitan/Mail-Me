from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
import json

mail = Blueprint('mail', __name__)

@mail.route('/inbox')
@login_required
def inbox():
     inbox_list = [
            # arr.array(mssgid: '123',
            #     sender: 'gerald@g.com',
            #     title:'This is email',
            #     subject: 'Subject',
            #     content: '<span>This is subject </span>'
            # )
        ]

     return render_template("client/inbox/inbox.html", user=current_user, inbox_list = inbox_list)

@mail.route('/inbox/<mssgid>', methods=['GET','POST'])
@login_required
def inboxmessage(mssgid):
     if request.method == 'POST':
          r_note = json.loads(request)
          if 'username' in session:
               session.pop('username', None)
          session['emails'] = r_note
         
     return render_template("client/inbox/message.html", user=current_user, id=mssgid)

   

@mail.route('/inbox/<mssgid>/reply')
@login_required
def inboxmessagereply(mssgid):
     page_id = request.args.get("id")
     page_g = request.args.get("g")
     if not page_id:
          page_id = ''
     if not page_g:
               page_g = ''

     if 'username' in session:
          username = session['username']

     data = {'id': page_id, 'gid': page_g}
     print(data)
     return render_template("client/inbox/reply.html", user=current_user, id=mssgid,data = data, username = username )



@mail.route('/inbox/email/session/<email>')
@login_required
def inboxmessagereplyemail(email):
     if 'username' in session:
          username = session['username']


     data = {'id': page_id, 'gid': page_g}
     print(data)
     return render_template("client/inbox/reply.html", user=current_user, id=mssgid,data = data, username = username )

@mail.route('/inbox/compose', methods=['GET','POST'])
@login_required
def compose():
     if request.method == 'POST':
          r_subject = request.form.get('subject')
          r_content = request.form.get('content')
          print(r_subject, r_content)
          flash('Email Send Successfuly', category='success')
          return redirect(url_for('mail.inbox'))
          
     return render_template("client/inbox/compose.html", user=current_user)


@mail.route('/spam')
@login_required
def spam():
     return render_template("client/spam.html", user=current_user)

@mail.route('/unsend')
@login_required
def unsend():
     return render_template("client/unsend.html", user=current_user)

