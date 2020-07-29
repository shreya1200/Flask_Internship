from flask import flash,render_template,url_for,Blueprint,redirect,request,session,logging
from flask_login import current_user,login_user,logout_user,login_required, login_manager,UserMixin
from Project import app,db,mail,loginmanager
from Project.users.forms import LoginForm,RegisterForm,ResetRequestForm,PasswordResetForm
from flask_mail import Message
from Project.models import User


users = Blueprint('users',__name__)
 

@users.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    # GET requests serve sign-up page.
    # POST requests validate form & user creation.
    if form.validate_on_submit(): #takes the information only when the all the validators are satisfied on submit
        user = User(
            name=form.name.data,
            email=form.email.data,
            number=form.number.data,
            username=form.username.data,
            password = form.password.data,
        )
        db.session.add(user)
        db.session.commit()  # Create new user
        print ('user added successfully')
        login_user(user)  # Log in as newly created user
        next = request.args.get('next')
        if next == None or not next[0] == '/':
            next = url_for('users.index')
        return redirect(next)
    return render_template('register.html',form=form)


@users.route('/login',methods=['GET','POST'])
def login():
    # if user is logged in after sign up
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user) 
            return redirect(url_for('users.index'))
        else:
            flash('Check Email and Password')
    return render_template('login.html',form=form)


@loginmanager.user_loader
def load_user(uid):
    # """Check if user is logged-in on every page load."""
    if uid is not None:
        return User.query.get(uid)
    return None


@loginmanager.unauthorized_handler
def unauthorized():
    # """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('users.login'))

@users.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('core.index'))

# route for our products tab
@users.route('/products')
def products():
    return render_template('products.html')


# route for pricing tab 
@users.route('/pricing')
def pricing():
    return render_template('pricing.html')


@users.route('/welcome')
def index():
    return render_template('welcome.html')


@users.route('/tts')
def tts():
    return render_template('tts.html')


@users.route('/transcribe')
def transcribe():
    return render_template('transcribe.html')


@users.route('/emotions')
def emotions():
    return render_template('emotions.html')

# route for contactus tab 
@users.route('/contactus')
def contactus():
    return render_template('contactus.html')


def send_reset_mail(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",sender= 'admin@anubhooti.com',recipients=[user.email])
    msg.body = f"To reset password visit following site\n\n{url_for('users.reset_password',token=token,_external=True)}\n\nIf you did not send request to reset password, simply ignore this message.\nRegards\nAnubhooti Solutions"
    mail.send(msg)

@users.route('/reset_request',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
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
        return redirect(url_for('users.index'))
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

