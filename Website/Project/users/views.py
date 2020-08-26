from flask import flash,render_template,url_for,Blueprint,redirect,request,session,logging,jsonify
from flask_login import current_user,login_user,logout_user,login_required, login_manager,UserMixin
from Project import app,db,mail,loginmanager
from Project.users.forms import LoginForm,RegisterForm,ResetRequestForm,PasswordResetForm,UpdateInfo,ChangePassword
from flask_mail import Message
from Project.models import User,Activity
import os
from mutagen.mp3 import MP3
import werkzeug
from werkzeug.utils import secure_filename
import soundfile as sf
import re
import stripe
from datetime import datetime,timedelta
import pathlib


users = Blueprint('users',__name__)
 
public = "pk_test_51HCJdAAB0pdFbVf1g2Lpev1JuHAkKSTLnJZWAJNvjcWFKXd806BRonbAilLwjMWikccDHPD67Sd1Olk9HTSbPxfK00iwPffxJP"
secret = "sk_test_51HCJdAAB0pdFbVf1JVaOwD2N7fuV1xWEAxARMRxKzPfZkgM414AgFAY7rgPekI9X0OrOf1ZGkGkeksPaAOh3shBl00ZLIaSpdq"

stripe.api_key = secret

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
            password = form.password.data,
            time_left= 10,
            words_left= 180
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
            global uid
            uid = current_user.id
            if user.account_type == 'admin':
                return redirect('/admin')
            else:
                return redirect(url_for('users.index'))
                
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
    user = User.query.get(current_user.id)
    time = datetime.now()
    if (time - user.subscription_time) > timedelta(days=30):
        user.membership = 'FREE'
        db.session.commit()
    return render_template('welcome.html',user=user)


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
        my_path = str(pathlib.Path().absolute()) + '\\upload_folder'

        mylist = os.listdir(my_path) # dir
        number_files = len(mylist)
        number_files = str(number_files+1)
        filename = "audio_" + str(current_user.id)+number_files + "_" + file.filename 
        create_file = filename

        print("Hiiii" + create_file)
        print(my_path)


        #file.save(my_path, secure_filename(filename))
        file.save("/upload_folder/", secure_filename(filename))
        a,b = os.path.splitext(filename)
        user = User.query.get(current_user.id)
        if(b=='.mp3'):
            audio = MP3(file)
            duration = (audio.info.length)/60   #in mins
        else:
            f = sf.SoundFile(file)
            duration = (len(f)/f.samplerate)/60 #in mins
        
        if(user.membership=='Individual'):
            if(duration>user.time_left):
                return redirect(url_for('users.subscribe'))
            else:
                #API call transcribe speech
                
                act = Activity(
                    time = datetime.utcnow(),
                    activity = 'transcribe speech',
                    input = str(pathlib.Path().absolute()) + '\\upload_folder' + create_file,
                    output = 'hi'
                )
                db.session.add(act)
                db.session.commit()

                user.words_left = (user.words_left-total_words)
                db.session.commit()
                print("Upload Successful!")
        elif(user.membership=='Institutional'):
            if(duration>user.time_left):
                return redirect(url_for('users.subscribe'))
            else:
                #API call transcribe speech
                act = Activity(
                    time = datetime.utcnow(),
                    activity = 'transcribe speech',
                    input = str(pathlib.Path().absolute()) + '\\upload_folder' + create_file,
                    output = 'hi'
                )
                db.session.add(act)
                db.session.commit()

                user.words_left = (user.words_left-total_words)
                db.session.commit()

                print("Upload Successful!")
        else:
            if(duration>user.time_left):
                return redirect(url_for('users.subscribe'))
            else:
                #API call transcribe speech
                act = Activity(
                    time = datetime.utcnow(),
                    activity = 'transcribe speech',
                    input = str(pathlib.Path().absolute()) + '\\upload_folder' + create_file,
                    output = 'hi'
                )
                db.session.add(act)
                db.session.commit()
                
                user.words_left = (user.words_left-total_words)
                db.session.commit()

                print("Upload Successful!")
    else:
        print("Try Again!")   

@users.route('/tts', methods=['GET', 'POST'])
def check():
    user = User.query.get(current_user.id)
    if request.method == 'POST':
        text1 = request.form['textinput']
        my_path = str(pathlib.Path().absolute()) + '\\upload_folder'
        list = os.listdir(my_path) # dir
        number_files = len(list)
        number_files = str(number_files+1)
        create_file = "upload_folder/file_"+str(user.id)+number_files+".txt"

        print("Hiiii" + create_file)
        print(my_path)
        
        f = open(create_file, "x")
        f.write(text1)
        f.close()

        total_words = int(len(re.findall(r'\w+', text1)))

        #if current user is a member then redirect to the page else redirect to payment page
        if(user.membership=="Individual"):
            #if member : individual
            if(total_words<=user.words_left):

                act = Activity(
                    time = datetime.utcnow(),
                    activity = 'text to speech',
                    input = str(pathlib.Path().absolute()) + '\\upload_folder' + create_file,
                    output = 'hi'
                )
                db.session.add(act)
                db.session.commit()

                user.words_left = (user.words_left-total_words)
                db.session.commit()

                return render_template('tts.html', input_text=text1)
            else:
                return redirect(url_for('users.subscribe'))
        elif(user.membership=="Institutional"):
            #if member : institutional
            if(total_words<=user.words_left):
                #API call tts

                act = Activity(
                    time = datetime.utcnow(),
                    activity = 'text to speech',
                    input = str(pathlib.Path().absolute()) + '\\upload_folder' + create_file,
                    output = 'hi'
                )
                db.session.add(act)
                db.session.commit()

                user.words_left = (user.words_left-total_words)
                db.session.commit()

                return render_template('tts.html', input_text=text1)
            else:
                return redirect(url_for('users.subscribe'))
        else:
            if(total_words<=user.words_left):
                #API call tts

                act = Activity(
                    time = datetime.utcnow(),
                    activity = 'text to speech',
                    input = str(pathlib.Path().absolute()) + '\\upload_folder' + create_file,
                    output = 'hi'
                )
                db.session.add(act)
                db.session.commit()

                user.words_left = (user.words_left-total_words)
                db.session.commit()

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
            customer_email = current_user.email,
            line_items = [
                {
                    "name": "Test Payment",
                    "currency": "inr",
                    "amount": "100000",
                    "quantity": 1
                }
            ]
        )
        global session_id 
        session_id = checkout_session["id"]
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
            customer_email = current_user.email,
            line_items = [
                {
                    "name": "Test Payment",
                    "currency": "inr",
                    "amount": "500000",
                    "quantity": 1
                }
            ]
        )
        global session_id 
        session_id = checkout_session["id"]
        return jsonify({"sessionId":checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403

@users.route('/success',methods=['GET'])
def success():
    user = User.query.get(uid)
    login_user(user)
    print(type(user))
    session = stripe.checkout.Session.retrieve(session_id)
    amount = 0
    time = datetime.now()
    if session["amount_total"] == 100000:
        user.membership = 'Individual'
        user.time_left = 120
        user.words_left = 2000
        user.subscription_time = time
        amount = 1000
    if session["amount_total"] == 500000:
        user.membership = 'Institutional'
        user.subscription_time = time
        user.time_left = 600
        user.words_left = 5000
        amount = 5000

    db.session.commit()
    return render_template('success.html',user=user,session=session,time=time,amount=amount)

@users.route('/cancelled')
def cancelled():
    return render_template('failed.html')

@users.route('/activity')
def activity():
    page = request.args.get('page',1,type=int)
    acts = Activity.query.filter_by(user_id=current_user.id).paginate(page=page,per_page=5)
    return render_template('activity.html',acts=acts)

@users.route('/settings')
def settings():
    return render_template('settings.html')

@users.route('/about',methods=['GET','POST'])
def about():
    success = False
    form = UpdateInfo()
    user = User.query.get(current_user.id)
    if form.validate_on_submit():
        user.name = form.name.data
        user.number = form.number.data
        db.session.commit()
        success = True
    if request.method == 'GET':
        form.name.data = user.name
        form.number.data = user.number
    return render_template('about.html',form=form,success=success)
    
@users.route('/password',methods=['GET','POST'])
def password():
    success = False
    incorrect = False
    form = ChangePassword()
    user = User.query.get(current_user.id)
    if form.validate_on_submit():
        if user.check_password(form.current_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            incorrect = False
            success = True
        else:
            incorrect = True
            success = False
    return render_template('password.html',form=form,success=success,incorrect=incorrect)
