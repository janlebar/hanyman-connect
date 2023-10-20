from flask import render_template, request, url_for
# from .app import items  # Import app and items from app.py
from app.models.database import BlogPost  # Import the BlogPost model from database.py
from flask import Blueprint, current_app
from app.constants.constants import items
from flask_mail import Mail
from flask_mail import Message
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session
from secrets import randbelow
from ..models.database import BlogApply, db, BlogPost, Category, Rating


posts_blueprint = Blueprint('posts', __name__)

# mail = Mail(posts_blueprint)
# POSTS    

@posts_blueprint.route('/posts', methods=['GET'])
def get_posts():
    if request.method == 'GET':
        blog_filter = BlogPost.confirmed == True
        all_posts = BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted).all()
        urls = {post.id: post.id for post in all_posts}
        return render_template('posts.html', posts=all_posts, urls=urls)

@posts_blueprint.route('/post/<string:id>', methods=['GET', 'POST'])
def get_post(id):
    all_posts = BlogPost.query.filter(BlogPost.id == id)
    urls = {post.id: post.id for post in all_posts}
    return render_template('posts.html', posts=all_posts, urls=urls)

@posts_blueprint.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    print(items)
    return render_template('new_post.html', items=items, action_url=url_for('posts.get_posts'))























# @app.route('/save_post', methods=['POST'])
# def save_post():
#     # if spodi ipolne form oz ga prebere
#     # POST /posts

#     post_title = request.form['title']
#     post_content = request.form['content']
#     post_offer = request.form['offer']
#     post_email = request.form['email']
#     post_longitude = request.form['longitude']
#     post_latitude = request.form['latitude']
#     post_item = request.form['item']  
#     post_confirmation_id = randbelow(2 ** 31)
#     post_phonenumber = request.form['phonenumber']
#     # session['email'] = post_email

#     for word in swear_words:
#         if word[:4].lower() in post_title.lower():
#                  return render_template('swearingnotallowed.html')

#     new_post = BlogPost(title=post_title,content=post_content,offer=post_offer,longitude=post_longitude,latitude=post_latitude,email=post_email,
#     confirmation_id=post_confirmation_id,category=post_item,phonenumber=post_phonenumber)

#     # vpise v bazo v trenutno
#     db.session.add(new_post)
#     # commit ga sele vpise permanentno v bazo
#     db.session.commit()
    
#     print("Latitude:", post_latitude)
#     print("Longitude:", post_longitude)


#     # poklical funkcijo sendmail in jo izpolnil z parametri iz posts
#     sendmail(post_email, post_confirmation_id)


#     try:
#         sendmail(post_email, post_confirmation_id)
#         flash('', "info")
#     except Exception as e:
#         flash("An error occurred while sending the email.", "error")
#         # Handle the error, maybe log it or display an error message
#     # vrne posodobljen posts page
#     return redirect('/posts')


# # posts mail function
# def sendmail(email, confirmation_id):
#     msg = Message('Confirm your post', sender='handytest753@gmail.com', recipients=[email])
#     # msg.body = f"Click to confirm {BASE_URL}/posts/confirm/{confirmation_id}"
#     confirmation_url = url_for("confirm", id=confirmation_id, _external=True)
    
#     msg.html = render_template(
#         'email_template.html',
#         confirmation_url=confirmation_url
#     )
#     mail.send(msg)

#     try:
#         with current_app.app_context():
#             mail.send(msg)
#         return True
#     except Exception as e:
#         print(e)
#         flash("Something went wrong while sending the email.")  # Flash this message on email sending failure
#         return redirect('/posts')  # Redirect to a suitable page after failure