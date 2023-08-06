from secrets import randbelow
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
# flask needs to import request, to get data from database
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session
from flask_migrate import Migrate
from flask_mail import Mail
from flask_mail import Message
from flask_hcaptcha import hCaptcha
from database import db, BlogPost, Category, BlogApply, Rating
from sqlalchemy import or_
from flask_babel import Babel
from flask_babel import gettext
# from transformers import pipeline
from datetime import datetime, timedelta


# # Load the text classification pipeline for hugging face
# model_name = "distilbert-base-uncased"
# classifier = pipeline("text-classification", model=model_name)


app = Flask(__name__)

babel = Babel(app)



# app config with private data excluded from git
app.config.from_pyfile('config.cfg')

db.init_app(app)

hcaptcha = hCaptcha(app)

# ORM is SQLAlchemy
migrate = Migrate(app, db)
# mail class
mail = Mail(app)

# serialiser config
secret_key = app.config.get("SECRET_KEY")
secret_salt = app.config.get("SECRET_SALT")
serializer = URLSafeTimedSerializer(secret_key)

swear_words = []  # Global variable to store the loaded list of swear words




def get_locale():
    return 'sl'



babel.init_app(app, locale_selector=get_locale)

# @babel.localeselector
# def get_locale():
#     # Check if the user explicitly selected a language
#     user_language = session.get('language')
#     if user_language is not None:
#         return user_language

#     # If the user didn't select a language, use the Accept-Language header from the browser
#     accept_languages = request.accept_languages.best_match(['en', 'sl'])
#     return accept_languages


@app.route('/change_language/<lang>')
def change_language(lang):
    # Assuming you are storing the language preference in the user's session
    session['language'] = lang
    return redirect(url_for('index'))














# LOCALIZE MAP
@app.route('/save_location', methods=['POST'])
def save_location():
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    
    # Save the values to the session
    session['longitude'] = longitude
    session['latitude'] = latitude
    
    return redirect(url_for('index'))












# INDEX

@app.route('/')
def index():
    # Retrieve longitude and latitude from session
    post_longitude_localisation = session.get('longitude')
    post_latitude_localisation = session.get('latitude')

    # Query the BlogPost objects
    blog_posts = BlogPost.query.all()

    coords = [{'id': post.id,
               'longitude': post.longitude,
               'latitude': post.latitude,
               'title': post.title,
               'post_longitude_localisation': post_longitude_localisation,
               'post_latitude_localisation': post_latitude_localisation}
              for post in blog_posts]

    return render_template('index.html', coords=coords)


# SWEARING PREWENTION

@app.before_first_request
def load_swear_words():
    global swear_words
    with open('swear_words.txt', 'r') as file:
        swear_words = [word.strip() for word in file.readlines()]

# SEARCH

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("query")

    if query:
        blog_filter = (
            (
                    # full text search # to_tsvector('slovenian', content) @@ to_tsquery('slovenian', 'stanovanje')
                    db.func.to_tsvector('slovenian', BlogPost.content).match(query, postgresql_regconfig='slovenian') |
                    db.func.to_tsvector('slovenian', BlogPost.title).match(query, postgresql_regconfig='slovenian') |
                    db.func.to_tsvector('slovenian', BlogPost.offer).match(query, postgresql_regconfig='slovenian') |

                    # partial match string
                    BlogPost.content.ilike(f'%{query}%') |

                    # filter blog categories
                    BlogPost.category.has(Category.name.ilike(f'%{query}%'))
             ) &
            (BlogPost.confirmed == True)
        )

        # print(BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted))
    else:
        blog_filter = BlogPost.confirmed == True

    # returns all posts drugace vrne prejsnje povste urejene po datumu query.order_by date_posted
    all_posts = BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted).all()

    # urls, dictionary, for all posts id that were queried above transformed with serialiser
    urls = {post.id: post.id for post in all_posts}
    return render_template('posts.html', posts=all_posts, urls=urls)

# POSTS    

@app.route('/posts', methods=['GET'])
def posts():
    if request.method == 'GET':
        blog_filter = BlogPost.confirmed == True

        # returns all posts otherwise returns previous posts ordered by date query.order_by date_posted
        all_posts = BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted).all()

        # urls, dictionary, for all posts id that were queried above transformed with serialiser
        urls = {post.id: post.id
                   for post in all_posts}
        return render_template('posts.html', posts=all_posts, urls=urls)

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    categories = Category.query.all()
    return render_template('new_post.html', categories=categories, action_url=url_for(posts.__name__))



@app.route('/save_post', methods=['POST'])
def save_post():
    # if spodi ipolne form oz ga prebere
    # POST /posts



    if not hcaptcha.verify():
        return redirect("/error?message=invalid captcha")
    post_title = request.form['title']
    post_content = request.form['content']
    post_offer = request.form['offer']
    post_email = request.form['email']
     # Retrieve longitude and latitude from session
    post_longitude = session.get('longitude')
    post_latitude = session.get('latitude')
    # post_longitude = request.form['longitude']
    # post_latitude = request.form['latitude']
    post_category_id = int(request.form["category"])
    post_confirmation_id = randbelow(2 ** 31)

    for word in swear_words:
        if word[:4].lower() in post_title.lower():
                 return render_template('swearingnotallowed.html')

    new_post = BlogPost(title=post_title, content=post_content, offer=post_offer,longitude = post_longitude, latitude = post_latitude,
                        email=post_email, category_id=post_category_id, confirmation_id=post_confirmation_id)

    # vpise v bazo v trenutno
    db.session.add(new_post)
    # commit ga sele vpise permanentno v bazo
    db.session.commit()

    # poklical funkcijo sendmail in jo izpolnil z parametri iz posts
    sendmail(post_email, post_confirmation_id)

    flash("Check mail!")

    # vrne posodobljen posts page
    return redirect('/posts')

# posts mail function
def sendmail(email, confirmation_id):
    msg = Message('Confirm your post', sender='handytest753@gmail.com', recipients=[email])
    msg.body = f"Click to confirm http://localhost:5000/posts/confirm/{confirmation_id}"
    msg.html = render_template('email_template.html', confirmation_id=confirmation_id)
    mail.send(msg)

# decorator funkcijo pokiče v ozadju. 
@app.route('/posts/confirm/<int:id>')
def confirm(id):
    """Confirm blog post by confirmation id created in POST /posts"""
    # get post from database where confirmation id matches or return 404
    post = BlogPost.query.filter(BlogPost.confirmation_id == id).first_or_404()
    # set post to confirmed
    post.confirmed = True
    # save and commit updated post to database
    db.session.add(post)
    db.session.commit()
    # add cokies session
    session["email"] = post.email

    # redirect to all posts
    # jaka: url_for je neke vrste funkcija ki generira raut in vzame parameter id, čeprav je string url
    return redirect(url_for('editing', id=post.id))

@app.route('/editing/<string:id>', methods=['GET', 'POST'])
def editing(id):
    # returns all posts query.order_by date_posted
    post = BlogPost.query.filter(BlogPost.id == id)
    return render_template('editing.html', posts=post)

    # rout za delete post
@app.route('/posts/delete/<string:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)

    if session.get("email") != post.email:
        raise Exception()
        
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')


# route za edit post, ker ga urejas mora bit metoda post ker jo shrani v bazo
@app.route('/posts/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    post = BlogPost.query.get_or_404(id)

    if post.email != session.get("email"):
        raise Exception("wrong email")
        
    categories = Category.query.all()

    if request.method == 'POST':
        post.title = request.form['title']
        post.offer = request.form['offer']
        post.content = request.form['content']
        post.email = request.form['email']
        post.category_id = request.form['category']
        db.session.commit()
        return redirect('/posts')
    else:
        # post=post ker rabi prebrisat prejsn povst
        return render_template('edit.html', post=post, categories=categories)

# POSTS WITH TIME LIMIT

@app.route('/post', methods=['GET'])
def post():
    # calculate the date from one month ago
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    # query for posts from the last month
    all_posts = BlogPost.query.filter(BlogPost.date_posted >= one_month_ago).all()
    # urls, dictionary, for all posts id that were queried above transformed with serializer
    urls = {post.id: post.id for post in all_posts}
    return render_template('posts.html', posts=all_posts, urls=urls)


# APPLYS


@app.route('/apply/new/<id>', methods=['GET', 'POST'])
def new_apply(id):
    return render_template('new_apply.html', blog_post_id=id, action_url=url_for(applys.__name__))

@app.route('/applys', methods=['GET', 'POST'])
def applys():
    # if spodi ipolne form oz ga prebere
    if request.method == 'POST':
        name_apply = request.form['name_apply']
        email_apply = request.form['email_apply']
        # # blog_post_id = request.form['blog_post_id']
        # blog_post_id = request.form['blog_post_id']
        apply_confirmation_id = randbelow(2 ** 31)
        # blog_post_id = serializer.loads(request.form['blog_post_id'], salt=secret_salt)
        blog_post_id = request.form['blog_post_id']
        new_apply = BlogApply(email_apply=email_apply, name_apply=name_apply, blog_post_id=blog_post_id,
                              apply_confirmation_id=apply_confirmation_id)

        # vpise v bazo v trenutno
        db.session.add(new_apply)
        # commit ga sele vpise permanentno v bazo
        db.session.commit()
        # add cokies session
        sendmailapply(email_apply, apply_confirmation_id)
        session['email_apply'] = email_apply
        return redirect('/posts')

def sendmailapply(email_apply, apply_confirmation_id):
    msg = Message('Hello', sender='handytest753@gmail.com', recipients=[email_apply])
    msg.body = f"Click to confirm http://localhost:5000/apply/confirmed/{apply_confirmation_id}"
    mail.send(msg)

@app.route('/apply/confirmed/<int:apply_confirmation_id>')
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
    return redirect(url_for('posts'))

def sendmailconnect(email_applys, emails, id_apply):
    msg = Message('Contact', sender='handytest753@gmail.com', recipients=[emails])
    msg.body = f"Please contact {email_applys} and rate by clicking http://localhost:5000/rating/{id_apply}"
    mail.send(msg)

# RATING APPLYS

@app.route('/rating/<uuid:id_apply>', methods=['GET', 'POST'])
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
        return redirect(url_for('posts'))


    return render_template('rating.html', apply=apply)


@app.route('/my_portfolio', methods=['GET'])
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_apply = request.form.get('email_apply')
        # Check if email exists in the database
        blog_apply = BlogApply.query.filter_by(email_apply=email_apply).first()
        if blog_apply:
            # Set email to session
            session['email_apply'] = email_apply
            return redirect(url_for('my_portfolio'))
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
    msg = Message('Hello', sender='handytest753@gmail.com', recipients=[email_apply])
    msg.body = f"Click to confirm http://localhost:5000/apply/confirmed/{apply_confirmation_id}"
    mail.send(msg)





# app.add_url_rule("/", None, view_func=index)




@app.route('/coords')
def test():
    BlogPosts = BlogPost.query.all()
    return jsonify([{'id': BlogPost.id,'longitude': BlogPost.longitude,'latitude': BlogPost.latitude, 'title': BlogPost.title, } for BlogPost in BlogPosts])


# jan naredil podstran
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


# jan naredil podstran
@app.route('/chmail', methods=['GET', 'POST'])
def chmail():
    return render_template('chmail.html')

# COOKIES 

@app.context_processor
def inject_template_scope():
    injections = dict()

    def cookies_check():
        value = request.cookies.get('cookie_consent')
        return value == 'true'

    injections.update(cookies_check=cookies_check)

    return injections

# TO SPODI JE ZATO DA LAUFA V DEBUG MODE
if __name__ == "__main__":
    app.run(debug=True)

