from flask import url_for,redirect
from Project import db,loginmanager,app
from werkzeug.security import generate_password_hash,check_password_hash
# UserMixin : By default, when a user is not actually logged in, current_user is set to an AnonymousUserMixin object.
from flask_login import UserMixin,current_user
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView



class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(50))
    number = db.Column(db.Integer())
    email = db.Column(db.String(50),unique=True,index=True)
    password_hash = db.Column(db.String(200))

    def set_password(self,password):
        self.password_hash = generate_password_hash(password,method='sha256')

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __init__(self,name,number,email,password):
        self.name = name
        self.number = number
        self.email = email
        self.password_hash = generate_password_hash(password)

    # def __repr__(self):
    #     return '<User {}>'.format(self.username)

    def get_reset_token(self,expires=300):
        s = Serializer(app.config['SECRET_KEY'],expires_in=expires)
        return s.dumps({'id':self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            id = s.loads(token)['id'] 
        except:
            return None
        return User.query.get(id)           

    # def __repr__(self):
    #     return f"Username: {self.username}\nEmail: {self.email}\n"


# class MyModelView(ModelView):                  #for /admin/user
#     def is_accessible(self):                    #if /login done,only then can proceed
#         return current_user.is_authenticated

#     # def inaccessible_callback(self, name, **kwargs):            //else redirect to login
#     #     return redirect(url_for('login')) 

class MyAdminIndexView(AdminIndexView):             #for /admin
    def is_accessible(self):
        return current_user.is_authenticated and int(current_user.get_id())==1

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login')) 

admin = Admin(app ,name='Admin', template_mode='bootstrap3',index_view = MyAdminIndexView())
admin.add_view(ModelView(User,db.session))    

@loginmanager.user_loader
def load_user(uid):
    return User.query.get(uid)

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    comment = db.Column(db.String(300))

    def __init__(self,name,email,comment):
        self.name = name
        self.email = email
        self.comment = comment