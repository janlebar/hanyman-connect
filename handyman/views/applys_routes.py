from flask import render_template, request, url_for
from flask import Blueprint, current_app
# from app.models.database import BlogApply  # Adjust the import path as needed
# from app.constants.constants import items
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session
from secrets import randbelow
from flask_mail import Mail, Message
from handyman.models.database import BlogApply, db, BlogPost, Category, Rating
from ..constants.constants import items




from handyman.views.utilities_routes import swear_words

applys_blueprint = Blueprint('applys', __name__)


# print(items)



# with current_app.app_context():
#     mail = Mail()
#     mail.send(msg)


# DELA SAM NE MAIL
# @applys_blueprint.route('/apply/new/<id>', methods=['GET', 'POST'])
# def new_apply(id):
#     # return render_template('new_apply.html', blog_post_id=id, action_url=url_for('applys.new_apply', id=id))
#     return render_template('new_apply.html', blog_post_id=id, action_url=url_for('applys.applys', id=id))

# @applys_blueprint.route('/applys', methods=['POST'])
# def applys():
#     if request.method == 'POST':
#         name_apply = request.form['name_apply']
#         email_apply = request.form['email_apply']
#         blog_post_id = request.form['blog_post_id']
#         apply_confirmation_id = randbelow(2 ** 31)

#         new_apply = BlogApply(email_apply=email_apply, name_apply=name_apply, blog_post_id=blog_post_id,
#                               apply_confirmation_id=apply_confirmation_id)

#         try:
#             send_mail_apply(email_apply, apply_confirmation_id)
#             flash('', 'info')
#         except Exception as e:
#             flash('An error occurred while sending the email.', 'error')
#             current_app.logger.error(str(e))  

#         db.session.add(new_apply)
#         db.session.commit()

#         return redirect('/posts')









# def send_mail_apply(email_apply, apply_confirmation_id):
#     with current_app.app_context():
#         mail = Mail()
    
#     msg = Message('Confirm your post', sender='handytest753@gmail.com', recipients=[email_apply])
#     mail.send(msg)
    
    
    
    
    

@applys_blueprint.route('/apply/new/<id>', methods=['GET', 'POST'])
def applys(id):
    if request.method == 'POST':
        name_apply = request.form['name_apply']
        email_apply = request.form['email_apply']
        blog_post_id = request.form['blog_post_id']
        apply_confirmation_id = randbelow(2 ** 31)

        new_apply = BlogApply(email_apply=email_apply, name_apply=name_apply, blog_post_id=blog_post_id,
                              apply_confirmation_id=apply_confirmation_id)

        db.session.add(new_apply)
        db.session.commit()
        
        send_mail_apply(email_apply, apply_confirmation_id)

        try:
            flash('', "info")
        except Exception as e:
            flash("An error occurred while sending the email.", "error")
            current_app.logger.error(str(e))
        return redirect('/posts')

    # If the request method is GET, render the form
    return render_template('new_apply.html', blog_post_id=id)




def send_mail_apply(email_apply, apply_confirmation_id):
    with current_app.app_context():
        mail = Mail()
        
        #confirmation_url = f"{BASE_URL}/apply/confirmed/{apply_confirmation_id}"
        # confirmation_url = url_for('confirmed', apply_confirmation_id=apply_confirmation_id, _external=True) -ZARADI BLUEPRINTOV NI PROV
        confirmation_url = url_for('applys.confirmed', apply_confirmation_id=apply_confirmation_id, _external=True)

        msg = Message('Confirm your post', sender='handytest753@gmail.com', recipients=[email_apply])
        msg.html = render_template('email_template_apply.html', confirmation_url=confirmation_url,
                                apply_confirmation_id=apply_confirmation_id)

        mail.send(msg)



















































@applys_blueprint.route('/apply/confirmed/<int:apply_confirmation_id>')
def confirmed(apply_confirmation_id):
    """Confirm blog post by confirmation id created in POST /posts"""
    # get post from database where confirmation id matches or return 404
    apply = BlogApply.query.filter(BlogApply.apply_confirmation_id == apply_confirmation_id).first_or_404()
    # set post to confirmed
    apply.apply_confirmed = True
    # save and commit updated post to database
    db.session.add(apply)
    db.session.commit()

    email_applys = ''.join(db.session.query(BlogPost.email).join(BlogApply).filter(
        BlogApply.apply_confirmation_id == apply_confirmation_id).first_or_404())

    emails = ''.join(db.session.query(BlogApply.email_apply).filter(
        BlogApply.apply_confirmation_id == apply_confirmation_id).first_or_404())

    sendmailconnect(email_applys, emails, apply.id_apply)
    return redirect(url_for('posts.get_posts'))


def sendmailconnect(email_applys, emails, id_apply):
    with current_app.app_context():
        mail = Mail()
    rate_link = url_for("applys.rating", id_apply=id_apply, _external=True)
   
    # rate_link = url_for("rating", id_apply=id_apply, _external=True)
    contact = email_applys
    subject = "Handyman connecting You with applicant"
    
    msg = Message(subject=subject, sender='handytest753@gmail.com', recipients=[emails])
    msg.html = render_template('email_template_connect.html', rate_link=rate_link, contact=contact)
    
    mail.send(msg)


# def sendmailconnect(email_applys, emails, id_apply):
#     msg = Message('Contact', sender='handytest753@gmail.com', recipients=[emails])
#     msg.body = f"Please contact {email_applys} and rate by clicking {BASE_URL}/rating/{id_apply}"
#     mail.send(msg)


# RATING APPLYS

@applys_blueprint.route('/rating/<uuid:id_apply>', methods=['GET', 'POST'])
def rating(id_apply):
    """Rate email_apply with stars 1 to 5"""
    apply = BlogApply.query.filter_by(id_apply=id_apply).first()
    if apply is None:
        abort(404)

    if request.method == 'POST':
        rating_value = int(request.form['rating'])
        rating = Rating(rating=rating_value, apply=apply)
        db.session.add(rating)
        db.session.commit()
        return redirect(url_for('posts.get_posts'))

    return render_template('rating.html', apply=apply)

@applys_blueprint.route('/my_portfolio', methods=['GET'])
def my_portfolio():
    # Get the email from the session
    email_apply_cookie = session.get('email_apply')

    # Check if the email exists in the BlogApply database
    apply = BlogApply.query.filter_by(email_apply=email_apply_cookie).first()

    if apply:
        ratings = [r[0] for r in db.session.query(Rating.rating)\
                            .join(BlogApply, BlogApply.id_apply == Rating.apply_id)\
                            .filter(BlogApply.email_apply == email_apply_cookie)\
                            .all()]
        # ratings = db.session.query(Rating)\
        #             .join(BlogApply, BlogApply.id_apply == Rating.apply_id)\
        #             .filter(BlogApply.email_apply == email_apply_cookie)\
        #             .all()

        # Render the my_portfolio template with the ratings
        return render_template('my_portfolio.html', ratings=ratings, email_apply_cookie=email_apply_cookie)
    else:
        # flash("No ratings found for this email.")
        # Redirect to the login template if the email is not found
        return redirect('login')


@applys_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_apply = request.form.get('email_apply')
        # Check if email exists in the database
        blog_apply = BlogApply.query.filter_by(email_apply=email_apply).first()
        if blog_apply:
            # Set email to session
            session['email_apply'] = email_apply
            return redirect(url_for('applys.my_portfolio'))
        else:
            # Email not found in database, handle expanded form fields
            name_apply = request.form.get('name_apply')
            blog_post_id = request.form.get('blog_post_id')
            apply_confirmation_id = randbelow(2 ** 31)
            new_apply = BlogApply(email_apply=email_apply, name_apply=name_apply, blog_post_id=blog_post_id, apply_confirmation_id=apply_confirmation_id)
            db.session.add(new_apply)
            db.session.commit()
            sendmailogin(email_apply, apply_confirmation_id)
            session['email_apply'] = email_apply
            return "Please check your email for confirmation"
    return render_template('login.html')

def sendmailogin(email_apply, apply_confirmation_id):
    with current_app.app_context():
        mail = Mail()
        
    msg = Message('Hello', sender='handytest753@gmail.com', recipients=[email_apply])
    #confirmation_url = f"{BASE_URL}/apply/confirmed/{apply_confirmation_id}"
    confirmation_url = url_for('confirmed', apply_confirmation_id=apply_confirmation_id)
    msg.body = f"Click to confirm {confirmation_url}"
    mail.send(msg)





# from flask import render_template, request, url_for
# from flask import Blueprint, current_app
# # from app.models.database import BlogApply  # Adjust the import path as needed
# # from app.constants.constants import items
# from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session
# from secrets import randbelow
# from flask_mail import Mail, Message
# from ..models.database import BlogApply, db, BlogPost, Category, Rating

# applys_blueprint = Blueprint('my_blueprint', __name__)

# @applys_blueprint.route('/applys', methods=['POST'])
# def applys():
#     if request.method == 'POST':
#         name_apply = request.form['name_apply']
#         email_apply = request.form['email_apply']
#         blog_post_id = request.form['blog_post_id']
#         apply_confirmation_id = randbelow(2 ** 31)

#         new_apply = BlogApply(email_apply=email_apply, name_apply=name_apply, blog_post_id=blog_post_id,
#                               apply_confirmation_id=apply_confirmation_id)

#         try:
#             send_mail_apply(email_apply, apply_confirmation_id)
#             flash('', 'info')
#         except Exception as e:
#             flash('An error occurred while sending the email.', 'error')
#             current_app.logger.error(str(e))

#         db.session.add(new_apply)
#         db.session.commit()

#         return redirect('/posts')

# def send_mail_apply(email_apply, apply_confirmation_id):
#     confirmation_url = url_for('confirmed', apply_confirmation_id=apply_confirmation_id, _external=True)
#     msg = Message('Confirm your post', sender=current_app.config['MAIL_USERNAME'], recipients=[email_apply])
#     msg.html = render_template('email_template_apply.html', confirmation_url=confirmation_url,
#                                apply_confirmation_id=apply_confirmation_id)
#     current_app.extensions['mail'].send(msg)
