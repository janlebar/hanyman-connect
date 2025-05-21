# app.py
import os

from logging.config import dictConfig
from secrets import randbelow
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
# flask needs to import request, to get data from database
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session, current_app
from flask_migrate import Migrate
from flask_mail import Mail
from flask_mail import Message
from flask_hcaptcha import hCaptcha
from handyman.models.database import db, BlogPost, Category, BlogApply, Rating
from sqlalchemy import or_,func
from flask_babel import Babel
from flask_babel import gettext
# from transformers import pipeline
from datetime import datetime, timedelta
from handyman.views.posts_routes import posts_blueprint
from handyman.views.applys_routes import applys_blueprint
# from handyman.views.utilities_routes import utilities_blueprint
from handyman.constants.constants import items



dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


# # Load the text classification pipeline for hugging face
# model_name = "distilbert-base-uncased"
# classifier = pipeline("text-classification", model=model_name)

app = Flask(__name__)
app.register_blueprint(posts_blueprint)
app.register_blueprint(applys_blueprint)
# app.register_blueprint(utilities_blueprint)
# Define BASE_URL directly in your code


# app config with private data excluded from git
app.config.from_pyfile('config.defaults.cfg')
app.config.from_pyfile('config.cfg', silent=True)
app.config.from_prefixed_env()

if os.getenv("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://" + os.getenv("DATABASE_URL").removeprefix("postgres://")

babel = Babel(app)

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

# swear_words = []  # Global variable to store the loaded list of swear words


items = []

def get_locale():
       # Check if the user explicitly selected a language
    user_language = session.get('language')
    print(user_language)
    if user_language is not None:
        return user_language

    # If the user didn't select a language, use the Accept-Language header from the browser
    accept_languages = request.accept_languages.best_match(['en', 'sl','es'])
    return accept_languages

babel.init_app(app, locale_selector=get_locale)

@app.before_request
def init_items():
    global items

    items = [
        gettext("Help Moving"),
        gettext("Yard Work"),
        gettext("Heavy Lifting"),
        gettext("Electrical help"),
        gettext("Snow Removal"),
        gettext("Lawn Care and Yard Work"),
        gettext("Pet Care"),
        gettext("Tech Help"),
        gettext("Childcare"),
        gettext("Elderly Assistance"),
        gettext("Car Wash and Detailing"),
        gettext("Painting and Repairs"),
        gettext("Tutoring"),
        gettext("Personal Shopping"),
        gettext("Plant Care"),
        gettext("House Sitting"),
        gettext("Legal assistance"),
        gettext("Permit assistance"),
        gettext("Other small work assistance")

    ]

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

@app.route('/', methods=['GET'])
def index():

    buttons = request.args.getlist("buttons")

    if buttons:
        filters = []

        for button in buttons:
            button_filter = (
                (
                    func.to_tsvector('slovenian', BlogPost.content).match(button, postgresql_regconfig='slovenian') |
                    func.to_tsvector('slovenian', BlogPost.title).match(button, postgresql_regconfig='slovenian') |
                    func.to_tsvector('slovenian', BlogPost.offer).match(button, postgresql_regconfig='slovenian') |
                    BlogPost.content.ilike(f'%{button}%') |
                    BlogPost.category.ilike(f'%{button}%')
                ) &
                (BlogPost.confirmed == True)
            )
            filters.append(button_filter)

        blog_filter = or_(*filters)
        all_posts = BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted).all()
        urls = {post.id: post.id for post in all_posts}
        return render_template('posts.html', posts=all_posts, urls=urls)
    else:
        # Retrieve longitude and latitude from session
        longitude_localisation = session.get('longitude')
        latitude_localisation = session.get('latitude')

        # Query the BlogPost objects
        blog_posts = BlogPost.query.filter(BlogPost.confirmed == True).all()

        coords = [{'id': post.id,
                   'longitude': post.longitude,
                   'latitude': post.latitude,
                   'title': post.title}
                  for post in blog_posts
                  if post.longitude and post.latitude]

        return render_template('index.html', coords=coords, longitude_localisation=longitude_localisation, latitude_localisation=latitude_localisation, items=items)

# SWEARING PREWENTION


# @app.before_first_request
# def load_swear_words():
#     global swear_words
#     with open('swear_words.txt', 'r') as file:
#         swear_words = [word.strip() for word in file.readlines()]

# SEARCH

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("query")

    if query:
        slovenian_full_text_search = (
            func.to_tsvector('slovenian', BlogPost.content).match(query, postgresql_regconfig='slovenian') |
            func.to_tsvector('slovenian', BlogPost.title).match(query, postgresql_regconfig='slovenian') |
            func.to_tsvector('slovenian', BlogPost.offer).match(query, postgresql_regconfig='slovenian') |
            func.to_tsvector('slovenian', BlogPost.category).match(query, postgresql_regconfig='slovenian')
        )
        
        english_full_text_search = (
            func.to_tsvector('english', BlogPost.content).match(query, postgresql_regconfig='english') |
            func.to_tsvector('english', BlogPost.title).match(query, postgresql_regconfig='english') |
            func.to_tsvector('english', BlogPost.offer).match(query, postgresql_regconfig='english') |
            func.to_tsvector('english', BlogPost.category).match(query, postgresql_regconfig='english')
        )

        partial_match = or_(
            BlogPost.content.ilike(f'%{query}%'),
            BlogPost.title.ilike(f'%{query}%'),
            BlogPost.offer.ilike(f'%{query}%'),
            BlogPost.category.ilike(f'%{query}%')
        )
        
        blog_filter = slovenian_full_text_search | english_full_text_search | partial_match
    else:
        blog_filter = BlogPost.confirmed == True

    all_posts = BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted).all()

    urls = {post.id: post.id for post in all_posts}
    return render_template('posts.html', posts=all_posts, urls=urls)


@app.route('/coords')
def test():
    BlogPosts = BlogPost.query.all()
    return jsonify([{'id': BlogPost.id,'longitude': BlogPost.longitude,'latitude': BlogPost.latitude, 'title': BlogPost.title, } for BlogPost in BlogPosts])

# ABOUT

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

# CHECK MAIL

# @app.route('/chmail', methods=['GET', 'POST'])
# def chmail():
#     return render_template('chmail.html')

# COOKIES 

@app.context_processor
def inject_template_scope():
    injections = dict()

    def cookies_check():
        value = request.cookies.get('cookie_consent')
        return value == 'true'

    injections.update(cookies_check=cookies_check)

    return injections

# DEBUG MODE

if __name__ == "__main__":
    app.run(debug=True)

