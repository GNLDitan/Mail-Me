from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import Messages, Receiver, Carboncopy, User
from . import db
import json

mail = Blueprint('mail', __name__)

@mail.route('/inbox')
@login_required
def inbox():
     inbox_list = []
     r_data = []
     receivers = Receiver.query.filter_by(email=current_user.email).all()
     for receiver in receivers:
          inbox = Messages.query.get(receiver.message_id)
          if (inbox):
              sender = User.query.get(inbox.sender_id)
              inbox_list.append({
                   'name': sender.first_name,
                   'subject': inbox.subject,
                   'date': inbox.date,
                   'isread': inbox.isread,
                   'message_id': inbox.id
              })
              
     print(inbox_list)
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
     if 'email' in session:
          s_email = session['email'] 
          s_email.append(email)
          session['email'] = s_email
     else:
          session['email'] = [email]

     return {}

@mail.route('/inbox/compose', methods=['GET','POST'])
@login_required
def compose():
     if request.method == 'POST':
          r_subject = request.form.get('subject')
          r_content = request.form.get('content')
          r_ccemail = request.form.get('ccemail')
          sender = current_user.id

          # add message
          message = Messages(sender_id = current_user.id, subject = r_subject, 
                             content = r_content, isread = False)
          db.session.add(message)
          db.session.commit()
          
          # add reciever
          if 'email' in session:
               for s_email in session['email']:
                  rcvr = Receiver(message_id = message.id, email = s_email)
                  db.session.add(rcvr)
           # add BCC
          rcvr = Carboncopy(message_id = message.id, email = r_ccemail)
          db.session.add(rcvr)
          db.session.commit()
      
          flash('Email Send Successfuly', category='success')
          return redirect(url_for('mail.inbox'))

     if request.method == 'GET':
          if 'email' in session:
               session.pop('email', None)
          
     return render_template("client/inbox/compose.html", user=current_user)


@mail.route('/spam')
@login_required
def spam():
     return render_template("client/spam.html", user=current_user)

@mail.route('/unsend')
@login_required
def unsend():
     return render_template("client/unsend.html", user=current_user)

