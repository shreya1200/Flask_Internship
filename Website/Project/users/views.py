from flask import flash,render_template,url_for,Blueprint,redirect,request
from flask_login import current_user,login_user,logout_user,login_required
from Project import app,db,mail
from Project.users.forms import LoginForm,RegisterForm,ResetRequestForm,PasswordResetForm
from flask_mail import Message
from Project.models import User

users = Blueprint('users',__name__)

@users.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("Logged In successfully.")
            next = request.args.get('next')
            if next == None or not next[0] == '/':
                next = url_for('user.index')
            return redirect(next)
    return render_template('login.html',form=form)

@users.route('/register',methods=['GET','POST'])
def register():
    pass

@users.route('/dashboard<uid>')
def index(uid):
    user = User.query.get(uid)
    return render_template('welcome.html',user=user)

def send_reset_mail(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",sender= 'admin@anubhooti.com',recipients=[user.email])
    msg.body = f"To reset password visit following site\n\n{url_for('users.reset_password',token=token,_external=True)}\n\nIf you did not send request to reset password, simply ignore this message.\nRegards\nAnubhooti Solutions"
    mail.send(msg)

@users.route('/reset_request',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.index',uid=current_user.uid))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_mail(user)
        flash(f"Password reset email sent to {user.email}",'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html',form=form)

@users.route('/reset/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.index',uid=current_user.uid))
    user = User.verify_token(token)
    if user is None:
        flash("Token invalid or expired.",'warning')
        return redirect(url_for('users.reset_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password changed successfully. Login to continue.",'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html',form=form)

