from datetime import datetime
from email.policy import default
from unicodedata import category
from secrets import randbelow

# v flask importas se request, ki je potreben da nov post poveze v bazo line 32
from flask import Flask, render_template, request, redirect, url_for
# TO SPODI JE SAM DA PYTHON POVLECE NOT KNJIZNICO ZA BAZO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Table
from sqlalchemy.orm import backref

from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
# TO SPODI JE SAM LOKACIJA ZA BAZO LAH ZAMENJAS BAZO ZA MYSQL (/// POMEN RELATIVNA POT DO BAZE)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

#mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'handytest753@gmail.com'
app.config['MAIL_PASSWORD'] = 'cldufworakfjudnp'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# TO SPODI JE SAM LOKACIJA ZA BAZO LAH ZAMENJAS BAZO ZA MYSQL (/// POMEN RELATIVNA POT DO BAZE)
db = SQLAlchemy(app)
session = db.session
migrate = Migrate(app, db)
#mail class
mail = Mail(app)


# this below is the structure for the table model. Table has columnes ,nullable=false 
# means it cannot be empty because if there is no content it cannot be created.
# if there is no author added then n/a
# datetime doesn't work without first importing it at the top aka from datetime import datetime
#JL

# spodaj baza za vrste del (parrent)
class Category(db.Model):

    __tablename__ = "work_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# model spodaj baza za blogpovste (child)
class BlogPost(db.Model):
    """Baza za poste"""

    __tablename__ = "blog_post"
    __mapper_args__ = {"eager_defaults": True}
    # false da ne sme bit prazna vrednost, default, kašna je vrednost če ni nič noter
    id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.String(100), nullable=False, default="")
    content = db.Column(db.Text, nullable=False, default="")
    offer = db.Column(db.Text, nullable=False, default="")
    email = db.Column(db.Text, nullable=False, default="")
    confirmation_id = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
#   za  kategorije
    category_id = db.Column(db.Integer, db.ForeignKey('work_type.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('work_type', lazy=True))

    def __repr__(self):
        """returns object representative JL"""
        return 'Blog post ' + str(self.id)


# DA NAREDIS BAZO GRES V TERMINAL NA LOKACIJO KJER BO IN NAPISES FROM APP IMPORT DB, KASNEJE DB.CREATE_ALL()
@app.route('/')
def index():
    return render_template('index.html')

#app.add_url_rule("/", None, view_func=index)

# naredil funkcijo ki pošlje mail
def sendmail(email,confirmation_id):
    msg = Message('Hello', sender = 'handytest753@gmail.com', recipients = [email])
    msg.body = f"Click to confirm http://localhost:5000/posts/confirm/{confirmation_id}"
    mail.send(msg)
#sendmail(confirmation_id="")


@app.route('/posts', methods=['GET', 'POST'])
def posts():
# if spodi ipolne form oz ga prebere 
    if request.method == 'POST':
        
        post_title = request.form['title']
        post_content = request.form['content']
        post_offer = request.form['offer']
        post_email = request.form['email']
        post_category_id = request.form["category"]
        post_confirmation_id = randbelow(10**12)
        new_post = BlogPost(title=post_title, content=post_content, offer=post_offer, 
                            email=post_email, category_id=post_category_id, confirmation_id=post_confirmation_id)

        # vpise v bazo v trenutno
        db.session.add(new_post)
        # commit ga sele vpise permanentno v bazo
        db.session.commit()

        #poklical funkcijo sendmail in jo izpolnil z parametri iz posts
        sendmail(post_email, post_confirmation_id)

        # vrne posodobljen posts page
        return redirect('/posts')
    else:
        # returns all posts drugace vrne prejsnje povste urejene po datumu query.order_by date_posted
        all_posts = BlogPost.query.filter(BlogPost.confirmed == True).order_by(BlogPost.date_posted).all()
        return render_template('posts.html', posts=all_posts)


# rout za delete post
@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')


# route za edit post, ker ga urejas mora bit metoda post ker jo shrani v bazo
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    post = BlogPost.query.get_or_404(id)
    # dodal kernc kategorije niso ble definiane z debugerjem
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




@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
        categories = Category.query.all()
        return render_template('new_post.html', categories=categories, action_url=url_for(posts.__name__))



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

    # redirect to all posts
    return redirect('/posts')
 


# jan naredil podstran
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

# jan naredil podstran
@app.route('/chmail', methods=['GET','POST'])
def chmail():
    return render_template('chmail.html')


# jan naredil podstran za main post
@app.route('/mainposts', methods=['GET', 'POST'])
def mainposts():
        # returns all posts query.order_by date_posted
        all_posts = BlogPost.query.filter(BlogPost.confirmed == True).order_by(BlogPost.date_posted).all()
        return render_template('mainposts.html', posts=all_posts)


# jan naredil podstran za main post
# @app.route('/editing/<int:id>', methods=['GET', 'POST'])
# def editing(id):
#      post = BlogPost.query.get_or_404(id)
# render_template('editing.html', )

@app.route('/editing/<int:id>', methods=['GET', 'POST'])
def editing(id):
        # returns all posts query.order_by date_posted
        id = BlogPost.query.filter(BlogPost.confirmed == True).all()
        return render_template('editing.html', posts=id)
#       post = BlogPost.query.get_or_404(id)


# @app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
# def edit(id):
    
#     post = BlogPost.query.get_or_404(id)
#     # dodal kernc kategorije niso ble definiane z debugerjem
#     categories = Category.query.all()

#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.offer = request.form['offer']
#         post.content = request.form['content']
#         post.email = request.form['email']
#         post.category_id = request.form['category']
#         db.session.commit()
#         return redirect('/posts')
#     else:
#         # post=post ker rabi prebrisat prejsn povst
#         return render_template('edit.html', post=post, categories=categories)



#     if request.method == 'POST':
        
#         post_title = request.form['title']
#         post_content = request.form['content']
#         post_offer = request.form['offer']
#         post_email = request.form['email']
#         post_category_id = request.form["category"]
#         post_confirmation_id = randbelow(10**12)
#         new_post = BlogPost(title=post_title, content=post_content, offer=post_offer, 
#                             email=post_email, category_id=post_category_id, confirmation_id=post_confirmation_id)

#         # vpise v bazo v trenutno
#         db.session.add(new_post)
#         # commit ga sele vpise permanentno v bazo
#         db.session.commit()

#         #poklical funkcijo sendmail in jo izpolnil z parametri iz posts
#         sendmail(post_email, post_confirmation_id)

#         # vrne posodobljen posts page
#         return redirect('/posts')
#     else:
#         # returns all posts drugace vrne prejsnje povste urejene po datumu query.order_by date_posted
#         all_posts = BlogPost.query.filter(BlogPost.confirmed == True).order_by(BlogPost.date_posted).all()
#         return render_template('posts.html', posts=all_posts)


# # rout za delete post
# @app.route('/posts/delete/<int:id>')
# def delete(id):
#     post = BlogPost.query.get_or_404(id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect('/posts')




# TO SPODI JE ZATO DA LAUFA V DEBUG MODE
if __name__ == "__main__":
    app.run(debug=True)
    


# QUERIES ZA BAZO PISES V TERMINAL: python3:from app import db,BlogPost 
# BlogPost.query.get()
#BlogPost.query.all() 
# BlogPost.query.filter_by(title='naslov').all()
# db.session.delete(BlogPost.query.get() )
# db.session.commit
# BlogPost.query.get().author = 'NOV AVTOR' -----TAKO SPREMENIS NPR AVTORJA
# db.session.commit