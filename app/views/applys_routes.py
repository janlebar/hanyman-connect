from flask import render_template, request, url_for
from flask import Blueprint, current_app
# from app.models.database import BlogApply  # Adjust the import path as needed
# from app.constants.constants import items
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session
from secrets import randbelow
from flask_mail import Mail, Message
from ..models.database import BlogApply, db, BlogPost, Category, Rating
from ..constants.constants import items

applys_blueprint = Blueprint('applys', __name__)




# Create a mail instance
mail = Mail()

# Define the function to load the email configuration
def load_mail_config():
    mail.init_app(current_app)
    current_app.config.from_pyfile('config.cfg', silent=True)


# with current_app.app_context():
#     mail = Mail()
#     mail.send(msg)



@applys_blueprint.route('/apply/new/<id>', methods=['GET', 'POST'])
def new_apply(id):
    return render_template('new_apply.html', blog_post_id=id, action_url=url_for('applys.new_apply', id=id))

@applys_blueprint.route('/applys', methods=['POST'])
def applys():
    if request.method == 'POST':
        name_apply = request.form['name_apply']
        email_apply = request.form['email_apply']
        blog_post_id = request.form['blog_post_id']
        apply_confirmation_id = randbelow(2 ** 31)

        new_apply = BlogApply(email_apply=email_apply, name_apply=name_apply, blog_post_id=blog_post_id,
                              apply_confirmation_id=apply_confirmation_id)

        try:
            send_mail_apply(email_apply, apply_confirmation_id)
            flash('', 'info')
        except Exception as e:
            flash('An error occurred while sending the email.', 'error')
            app.logger.error(str(e))  

        db.session.add(new_apply)
        db.session.commit()

        return redirect('/posts')

def send_mail_apply(email_apply, apply_confirmation_id):
    #confirmation_url = f"{BASE_URL}/apply/confirmed/{apply_confirmation_id}"
    confirmation_url = url_for('confirmed', apply_confirmation_id=apply_confirmation_id, _external=True)
    msg = Message('Confirm your post', sender='handytest753@gmail.com', recipients=[email_apply])
    msg.html = render_template('email_template_apply.html', confirmation_url=confirmation_url,
                               apply_confirmation_id=apply_confirmation_id)
    mail.send(msg)