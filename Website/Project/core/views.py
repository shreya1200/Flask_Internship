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