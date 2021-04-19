from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import Messages, Receiver, Carboncopy, User
from bs4 import BeautifulSoup
from . import db
import json
import requests
import os

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
                   'id': inbox.id,
                   'name': sender.first_name,
                   'subject': inbox.subject,
                   'date': inbox.date,
                   'isread': inbox.isread,
                   'message_id': inbox.id,
                   'content': inbox.content
              })
     return render_template("client/inbox/inbox.html", user=current_user, inbox_list = inbox_list)

@mail.route('/inbox/<mssgid>', methods=['GET','POST'])
@login_required
def inboxmessage(mssgid):
     threads = []
     inbox = Messages.query.get(mssgid)
     sender = User.query.get(inbox.sender_id)
     reply_id = inbox.id
     
     message_data = { 
          'id': inbox.id,
          'subject': inbox.subject,
          'email': sender.email,
          'name': sender.first_name,
          'img_src': os.path.join(os.getenv("IMG_SRC"),'email.jpg'),
          'threads': []
     }

     # Get Thread Reply Id
     while reply_id:
           threads.append({
               'id': inbox.id,
               'name': sender.first_name,
               'email': sender.email,
               'subject': inbox.subject,
               'date': inbox.date,
               'content': inbox.content,
               'reply_id': reply_id,
               'img_src': os.path.join(os.getenv("IMG_SRC"),'email.jpg')
           })
           reply_id = inbox.reply_id
           inbox = Messages.query.get(reply_id)
           sender = Messages.query.get(mssgid)

     message_data['threads'] = threads

     if 'reply' in session:
          session.pop('reply', None)

     session['reply'] = message_data

     return render_template("client/inbox/message.html", user=current_user, message_data=message_data)

   

@mail.route('/inbox/reply')
@login_required
def inboxmessagereply():
    
     if 'reply' in session:
          message_data = session['reply']

     print(message_data)
     return render_template("client/inbox/reply.html", user=current_user, message_data = message_data )



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
          r_receiver = request.form.get('receiver')

          sender = current_user.id

          # add message
          message = Messages(sender_id = current_user.id, subject = r_subject, 
                             content = r_content, isread = False)
          db.session.add(message)
          db.session.commit()

          # add user reciever
          if 'email' in session:
               # catch for event 
               p_email = session['email'] 
               p_email.append(r_receiver)
               session['email'] = p_email
               for s_email in session['email']:
                  rcvr = Receiver(message_id = message.id, email = s_email)
                  db.session.add(rcvr)
          else:
               s_rcvr = Receiver(message_id = message.id, email = r_receiver)
               db.session.add(s_rcvr)

          # add user BCC
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


# all email send must be send here
@mail.route('/auth/sendemail', methods=['GET','POST'])
@login_required
def sendemail():
   if request.method == 'POST':
          r_subject = request.form.get('subject')
          r_content = request.form.get('content')
          r_ccemail = request.form.get('ccemail')
          r_receiver = request.form.get('receiver')

          sender = current_user.id

          # add message
          message = Messages(sender_id = current_user.id, subject = r_subject, 
                             content = r_content, isread = False)
          db.session.add(message)
          db.session.commit()

          # add user reciever
          if 'email' in session:
               # catch for event 
               p_email = session['email'] 
               p_email.append(r_receiver)
               session['email'] = p_email
               for s_email in session['email']:
                  rcvr = Receiver(message_id = message.id, email = s_email)
                  db.session.add(rcvr)
          else:
               s_rcvr = Receiver(message_id = message.id, email = r_receiver)
               db.session.add(s_rcvr)

          # add user BCC
          rcvr = Carboncopy(message_id = message.id, email = r_ccemail)
          db.session.add(rcvr)
          db.session.commit()

          flash('Email Send Successfuly', category='success')
          return redirect(url_for('mail.inbox'))
