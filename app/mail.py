from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import Messages, Receiver, Carboncopy, User
from operator import attrgetter, itemgetter
from . import db
from bs4 import BeautifulSoup
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
              _cont = ''

              soup = BeautifulSoup(inbox.content, 'html.parser')
              par = soup.find_all('p')
              if (par) and len(par) > 0:
                   _cont = par[0].text
              else:
                   _cont = '<span><span>'

              inbox_list.append({
                   'id': inbox.id,
                   'name': sender.first_name,
                   'subject': inbox.subject,
                   'date': inbox.date,
                   'isread': inbox.isread,
                   'message_id': inbox.id,
                   'content': inbox.content,
                   'p_content': _cont
              })

     inbox_list = sorted(inbox_list, key=itemgetter('date'), reverse=True)
  
     return render_template("client/inbox/inbox.html", user=current_user, inbox_list = inbox_list)

@mail.route('/inbox/<mssgid>', methods=['GET','POST'])
@login_required
def inboxmessage(mssgid):
     threads = []
     inbox = Messages.query.get(mssgid)
     sender = User.query.get(inbox.sender_id)
     reply_id = inbox.reply_id

     # set inbox as read
     inbox.isread = True
     db.session.commit()

     message_data = { 
          'id': inbox.id,
          'subject': inbox.subject,
          'email': sender.email,
          'name': sender.first_name,
          'img_src': os.path.join(os.getenv("IMG_SRC"),'email.jpg'),
          'threads': []
     }
 
     # Get Thread Reply Id
     while (inbox):
           thread = {
               'id': inbox.id,
               'name': sender.first_name,
               'email': sender.email,
               'subject': inbox.subject,
               'date': inbox.date,
               'content': inbox.content,
               'reply_id': reply_id,
               'img_src': os.path.join(os.getenv("IMG_SRC"),'email.jpg'),
               'email_to': []
           }
           
           # check all receiver of email
           receiver = Receiver.query.filter_by(message_id=inbox.id).all()
           email_to = []
           if (receiver):
               for rcvr in receiver:
                    if not (rcvr.email in email_to) and rcvr.email != sender.email:
                       r_user = User.query.filter_by(email=rcvr.email).first()
                       if (r_user):
                         email_to.append({
                              'email': rcvr.email,
                              'name': r_user.first_name
                         })
             
               if (len(email_to) > 0):
                    thread['email_to'] = email_to

           threads.append(thread)
           reply_id = inbox.reply_id
           inbox = Messages.query.get(reply_id)
           if (inbox):
               sender = User.query.get(inbox.sender_id)

     message_data['threads'] = threads

     if 'session_reply' in session:
          session.pop('session_reply', None)

     session['session_reply'] = message_data

     return render_template("client/inbox/message.html", user=current_user, message_data=message_data)

   

@mail.route('/inbox/reply')
@login_required
def inboxmessagereply():
     s_email = []
     if 'session_reply' in session:
          message_data = session['session_reply']
          
          for thread in message_data['threads']:
               email_to = thread['email_to']

               if not (thread['email'] in s_email) and current_user.email != thread['email']:
                         s_email.append(thread['email'])
           
               # reply all to and cc
               for m_t in email_to:
                    if not (m_t['email'] in s_email) and current_user.email != m_t['email']:
                         s_email.append(m_t['email'])

     if  (len(s_email)):
           session['session_email'] = s_email

     return render_template("client/inbox/reply.html", user=current_user, message_data = message_data, s_email = s_email )



@mail.route('/inbox/email/session/<email>')
@login_required
def inboxmessagereplyemail(email):
     if 'session_email' in session:
          s_email = session['session_email'] 
          s_email.append(email)
          session['session_email'] = s_email
     else:
          session['session_email'] = [email]

     return {}

@mail.route('/inbox/compose', methods=['GET','POST'])
@login_required
def compose():
      # clear session
     if 'session_email' in session:
          session.pop('session_email', None)
     
     # if has session for reply
     if 'session_reply' in session:
          session.pop('session_reply', None)

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
@mail.route('/auth/sendemail', methods=['POST'])
@login_required
def sendemail():
   if request.method == 'POST':
          reply_id = 0
          r_subject = request.form.get('subject')
          r_content = request.form.get('content')
          r_ccemail = request.form.get('ccemail')
          r_receiver = request.form.get('receiver')

          # if has session for reply
          if 'session_reply' in session:
               reply_id =  session['session_reply']['id']
              

          sender = current_user.id

          # add message
          message = Messages(sender_id = current_user.id, subject = r_subject, 
                             content = r_content, isread = False, reply_id = reply_id)
          db.session.add(message)
          db.session.commit()

          # add user reciever
          if 'session_email' in session:
               # catch for event 
               p_email = session['session_email'] 
               p_email.append(r_receiver)
               session['session_email'] = p_email
               for s_email in session['session_email']:
                  #ToDo: find if user exists
                  #if not send to unsent (must create template) 
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
          if 'session_email' in session:
               session.pop('session_email', None)
          return redirect(url_for('mail.inbox'))
