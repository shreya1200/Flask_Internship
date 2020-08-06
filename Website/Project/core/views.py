from flask import render_template,url_for,Blueprint,redirect,request
from Project.core.forms import FeedbackForm
from Project.models import Feedback
from Project import db

core = Blueprint('core',__name__)

@core.route('/')
def index():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(form.name.data,form.email.data,form.comment.data)
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('core.index'))
    return render_template('index.html',form=form)

# route for our products tab
@core.route('/products')
def products():
    return render_template('products.html')


# route for pricing tab 
@core.route('/pricing')
def pricing():
    return render_template('pricing.html')

# route for contactus tab 
@core.route('/contactus')
def contactus():
    return render_template('contactus.html')
