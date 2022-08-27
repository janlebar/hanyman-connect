from datetime import datetime
from email.policy import default
from unicodedata import category

# v flask importas se request, ki je potreben da nov post poveze v bazo line 32
from flask import Flask, render_template, request, redirect
# TO SPODI JE SAM DA PYTHON POVLECE NOT KNJIZNICO ZA BAZO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Table

app = Flask(__name__)
# TO SPODI JE SAM LOKACIJA ZA BAZO LAH ZAMENJAS BAZO ZA MYSQL (/// POMEN RELATIVNA POT DO BAZE)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

db = SQLAlchemy(app)
session = db.session
migrate = Migrate(app, db)

# TO SPODI JE STRUKTURA ZA BAZO MODEL, DELA SE Z CLASSI? BAZA MA TKO K TABELA COLUMNE, NULLABLE=FALSE POMENI DA NE MORE BIT PRAZN KER CE NI KONTENTA NE MORE BIT POVSTA
# CE AVTORJA NI GA DODA KOT N/A
# DATETIME NE DELUJE BREZ DA GA PREJ NA VRHU NE IMPORTERAS AKA FROM DATETIME IMPORT DATETIME

from sqlalchemy.orm import backref







# spodaj baza za vrste del (parrent)
class Category(db.Model):

    __tablename__ = "work_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# spodaj baza za blogpovste (child)
class BlogPost(db.Model):

    __tablename__ = "blog_post"
    __mapper_args__ = {"eager_defaults": True}
    
    id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.String(100), nullable=False, default="")
    content = db.Column(db.Text, nullable=False, default="")
    offer = db.Column(db.Text, nullable=False, default="")
    email = db.Column(db.Text, nullable=False, default="")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
#   za  kategorije
    category_id = db.Column(db.Integer, db.ForeignKey('work_type.id'),
        nullable=True)
    category = db.relationship('Category',
        backref=db.backref('work_type', lazy=True))






# KREIRA OBJEKT V BAZI IN DA ID
    def __repr__(self):
        return 'Blog post ' + str(self.id)
# DA NAREDIS BAZO GRES V TERMINAL NA LOKACIJO KJER BO IN NAPISES FROM APP IMPORT DB, KASNEJE DB.CREATE_ALL()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts', methods=['GET', 'POST'])
def posts():
# if spodi ipolne form oz ga prebere 
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_offer = request.form['offer']
        post_email = request.form['email']
        post_category_id = request.form["category"]
        new_post = BlogPost(title=post_title, content=post_content, offer=post_offer, email=post_email, category_id=post_category_id)


# vpise v bazo v trenutno
        db.session.add(new_post)
# commit ga sele vpise permanentno v bazo
        db.session.commit()
# vrne posodobljen posts page
        return redirect('/posts')
    else:
# drugace vrne prejsnje povste urejene po datumu query.order_by date_posted
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        return render_template('posts.html', posts=all_posts)
# rout za delete post
@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')
# rout za edit post, ker ga urejas mora bit metoda post ker jo shrani v bazo
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.offer = request.form['offer']
        post.content = request.form['content']
        post.email = request.form['email']
        db.session.commit()
        return redirect('/posts')
    else:
# post=post ker rabi prebrisat prejsn povst
        return render_template('edit.html', post=post)

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post.title = request.form['title']
        post.offer = request.form['offer']
        post.content = request.form['content']
        post.email = request.form['email']
        new_post = BlogPost(title=post_title, content=post_content, offer=post_offer, email=post_email)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
# jaka naredil da naredi categorije poizvedbo za vse 
        categories = Category.query.all()
        return render_template('new_post.html', categories=categories)

# jan naredil podstran
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')



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