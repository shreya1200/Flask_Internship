from flask import flash,render_template,url_for,Blueprint,redirect,request,session,logging,jsonify
from flask_login import current_user,login_user,logout_user,login_required, login_manager,UserMixin
from Project import app,db,mail,loginmanager
from Project.users.forms import LoginForm,RegisterForm,ResetRequestForm,PasswordResetForm
from flask_mail import Message
from Project.models import User
from validate_email import validate_email
import os
from mutagen.mp3 import MP3
import werkzeug
import soundfile as sf
import re
import stripe

users = Blueprint('users',__name__)
 
public = "pk_test_51HCJdAAB0pdFbVf1g2Lpev1JuHAkKSTLnJZWAJNvjcWFKXd806BRonbAilLwjMWikccDHPD67Sd1Olk9HTSbPxfK00iwPffxJP"
secret = "sk_test_51HCJdAAB0pdFbVf1JVaOwD2N7fuV1xWEAxARMRxKzPfZkgM414AgFAY7rgPekI9X0OrOf1ZGkGkeksPaAOh3shBl00ZLIaSpdq"

stripe.api_key = secret

@users.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    is_valid = validate_email(str(form.email.data),verify=True)
    print(is_valid)
    # GET requests serve sign-up page.
    # POST requests validate form & user creation.
    if form.validate_on_submit() and is_valid==True: #takes the information only when the all the validators are satisfied on submit
        user = User(
            name=form.name.data, 
            email=form.email.data,
            number=form.number.data,
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
    # print(current_user)
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user) 
            if int(current_user.get_id())!=1:
                print(current_user.get_id())
                print(type(current_user.get_id()))
                return redirect(url_for('users.index'))
            else:
                return redirect('/admin')
                #return render_template('/admin')

           # return redirect(url_for('users.index'))
        else:
            flash('Incorrect email or password.')
    return render_template('login.html',form=form)


@loginmanager.user_loader
def load_user(uid):
    # Check if user is logged-in on every page load.
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


@users.route('/upload',methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['myFile']
        filename = file.filename
        a,b = os.path.splitext(filename)
        if(b=='.mp3'):
            audio = MP3(file)
            duration = (audio.info.length)/60   #in mins
        else:
            f = sf.SoundFile(file)
            duration = (len(f)/f.samplerate)/60 #in mins
        
        if(current_user.membership=='Individual'):
            if(duration>120):
                return redirect(url_for('users.subscribe'))
            else:
                #API call
                print("Upload Successful!")
        elif(current_user.membership=='Institutional'):
            if(duration>600):
                return redirect(url_for('users.subscribe'))
            else:
                #API call
                print("Upload Successful!")
        else:
            if(duration>10):
                return redirect(url_for('users.subscribe'))
            else:
                #API call
                print("Upload Successful!")
    else:
        print("Try Again!")   

@users.route('/tts', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        text1 = request.form['textinput']
        total_words = int(len(re.findall(r'\w+', text1)))

        #if current user is a member then redirect to the page else redirect to payment page
        if(current_user.membership=="Individual"):
            #if member : individual
            if(total_words<=5000):
                #API call
                return render_template('tts.html', input_text=text1)
            else:
                return redirect(url_for('users.subscribe'))
        elif(current_user.membership=="Institutional"):
            #if member : institutional
            if(total_words<=10000):
                #API call
                return render_template('tts.html', input_text=text1)
            else:
                return redirect(url_for('users.subscribe'))
        else:
            if(total_words<=180):
                #API call
                return render_template('tts.html', input_text=text1)
            else:
                return redirect(url_for('users.subscribe'))

@users.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

@users.route("/config")
def config():
    stripe_config = {"publicKey": public}
    return jsonify(stripe_config)

@users.route('/charge_individual')
def charge_individual():
    domainUrl = "http://localhost:5000/"
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url = domainUrl + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url = domainUrl + "cancelled",
            payment_method_types = ['card'],
            mode = "payment",
            line_items = [
                {
                    "name": "Test Payment",
                    "currency": "inr",
                    "amount": "100000",
                    "quantity": 1
                }
            ]
        )
        return jsonify({"sessionId":checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403

@users.route('/charge_institutional')
def charge_institutional():
    domainUrl = "http://localhost:5000/"
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url = domainUrl + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url = domainUrl + "cancelled",
            payment_method_types = ['card'],
            mode = "payment",
            line_items = [
                {
                    "name": "Test Payment",
                    "currency": "inr",
                    "amount": "500000",
                    "quantity": 1
                }
            ]
        )
        return jsonify({"sessionId":checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403

@users.route('/success')
def success():
    return render_template('success.html')

@users.route('/cancelled')
def cancelled():
    return render_template('failed.html')

    
