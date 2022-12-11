from datetime import datetime
from email.policy import default
from unicodedata import category
from secrets import randbelow
from webbrowser import get
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# v flask importas se request, ki je potreben da nov post poveze v bazo 
from flask import Flask, render_template, request, redirect, url_for
# TO SPODI JE SAM DA PYTHON POVLECE NOT KNJIZNICO ZA BAZO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Index, text
from sqlalchemy.orm import backref

from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
# app config with private data excluded from git
app.config.from_pyfile('config.cfg')

# DA NAREDIS BAZO GRES V TERMINAL NA LOKACIJO KJER BO IN NAPISES FROM APP IMPORT DB, KASNEJE DB.CREATE_ALL()
db = SQLAlchemy(app)
sessiondb = db.session
migrate = Migrate(app, db)
#mail class
mail = Mail(app)

serializer = URLSafeTimedSerializer('Thisisasecret!')

# this below is the structure for the table model. Table has columnes ,nullable=false
# means it cannot be empty because if there is no content it cannot be created.
# if there is no author added then n/a
# datetime doesn't work without first importing it at the top aka from datetime import datetime
#JL

def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return db.func.to_tsvector('slovenian', text(s))

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

    # create full text search index
    __table_args__ = (
        Index(
            'idx_fulltext_title',
            db.func.to_tsvector('slovenian', title),
            postgresql_using='gin'
        ),
        Index(
            'idx_fulltext_content',
            db.func.to_tsvector('slovenian', content),
            postgresql_using='gin'
        ),
        Index(
            'idx_fulltext_offer',
            db.func.to_tsvector('slovenian', offer),
            postgresql_using='gin'
        ),
    )

    def __repr__(self):
        """returns object representative JL"""
        return 'Blog post ' + str(self.id)

class BlogApply(db.Model):
    """Baza za apply"""

    __tablename__ = "blog_apply"
    __mapper_args__ = {"eager_defaults": True}
    id_apply = db.Column(db.Integer, primary_key=True,)
    name_apply = db.Column(db.Text, nullable=False, default="")
    email_apply = db.Column(db.Text, nullable=False, default="")
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))
    apply_confirmation_id = db.Column(db.Integer, nullable=False)
    apply_confirmed = db.Column(db.Boolean, default=False)

    # confirmation_id_apply = db.Column(db.Integer, nullable=False)
    # confirmed_apply = db.Column(db.Boolean, default=False)
#   za  kategorije

    def __repr__(self):
        """returns object representative JL"""
        return 'Blog apply ' + str(self.id_apply)


@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
        categories = Category.query.all()
        return render_template('new_post.html', categories=categories, action_url=url_for(posts.__name__))

@app.route('/posts', methods=['GET', 'POST'])
def posts():
# if spodi ipolne form oz ga prebere
    # POST /posts
    if request.method == 'POST':

        post_title = request.form['title']
        post_content = request.form['content']
        post_offer = request.form['offer']
        post_email = request.form['email']
        post_category_id = int(request.form["category"])
        post_confirmation_id = randbelow(10**10)



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

    # GET /posts?query=stanovanje
    else:
        # /posts?query=stanovanje
        query = request.args.get("query")

        #       all_posts = BlogPost.query.filter(
        #             # to_tsvector('slovenian', content) @@ to_tsquery('slovenian', 'stanovanje')
        #            db.func.to_tsvector('slovenian', BlogPost.content).match(query, postgresql_regconfig='slovenian') &
        #            (BlogPost.confirmed == True)).order_by(BlogPost.date_posted).all()

        if query:
            blog_filter = (
                # to_tsvector('slovenian', content) @@ to_tsquery('slovenian', 'stanovanje')
                db.func.to_tsvector('slovenian', BlogPost.content).match(query, postgresql_regconfig='slovenian') &
                (BlogPost.confirmed == True)
            )
        else:
            blog_filter = BlogPost.confirmed == True

        # returns all posts drugace vrne prejsnje povste urejene po datumu query.order_by date_posted
        all_posts = BlogPost.query.filter(blog_filter).order_by(BlogPost.date_posted).all()

        # urls, dictionary, for all posts id that were queried above transformed with serialiser
        urls = {post.id: serializer.dumps(post.id, salt=MY_WEB_APP)
                for post in all_posts}
        return render_template('posts.html', posts=all_posts, urls=urls)

MY_WEB_APP = 'asdasd'

# naredil funkcijo ki pošlje mail
def sendmail(email,confirmation_id):
    msg = Message('Hello', sender = 'handytest753@gmail.com', recipients = [email])
    msg.body = f"Click to confirm http://localhost:5000/posts/confirm/{confirmation_id}"
    mail.send(msg)
#sendmail(confirmation_id="")

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
    #jaka: url_for je neke vrste funkcija ki generira raut in vzame parameter id, čeprav je string url
    return redirect (url_for('editing', id=post.id))


@app.route('/apply/new/<id>', methods=['GET', 'POST'])
def new_apply(id):
        # wtf why dumps works and load does not?
        return render_template('new_apply.html', blog_post_id=id, action_url=url_for(applys.__name__))

# @app.route('/apply/new/<int:id>', methods=['GET', 'POST'])
# def new_apply(id):
#         # urls = {post.id: serializer.dumps(post.id, salt=MY_WEB_APP)
#         blog_post_id = serializer.load(post.id, salt=MY_WEB_APP)
#         return render_template('new_apply.html',blog_post_id=blog_post_id, action_url=url_for(applys.__name__))

@app.route('/applys', methods=['GET', 'POST'])
def applys():
# if spodi ipolne form oz ga prebere
    if request.method == 'POST':
        name_apply = request.form['name_apply']
        email_apply = request.form['email_apply']
        # # blog_post_id = request.form['blog_post_id']
        # blog_post_id = request.form['blog_post_id']
        apply_confirmation_id = randbelow(10**12)
        blog_post_id = serializer.loads(request.form['blog_post_id'], salt=MY_WEB_APP)
        new_apply = BlogApply( email_apply=email_apply,name_apply=name_apply,blog_post_id=blog_post_id,apply_confirmation_id=apply_confirmation_id)

        # vpise v bazo v trenutno
        db.session.add(new_apply)
        # commit ga sele vpise permanentno v bazo
        db.session.commit()
        sendmailapply(email_apply,apply_confirmation_id)
        return redirect('/posts')
# SAMO VPIŠE V BAZO NE VRNE APPLYS KER GA NOČEŠ VIDET
    #     return redirect('/v povste ')

def sendmailapply(email_apply,apply_confirmation_id):
    msg = Message('Hello', sender = 'handytest753@gmail.com', recipients = [email_apply])
    msg.body = f"Click to confirm http://localhost:5000/apply/confirmed/{apply_confirmation_id}"
    mail.send(msg)

# decorator funkcijo pokiče v ozadju.
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

    # results=session.query(BlogPost).join(BlogApply).filter(BlogApply.apply_confirmation_id == apply_confirmation_id)
    # for result in results:

    #     print(result)
    # results = sessiondb.query(BlogPost.email).join(BlogApply).filter(BlogApply.apply_confirmation_id == apply_confirmation_id)
    # for result in results:
    #     print(result)
    # names = sessiondb.query(BlogPost.title).join(BlogApply).filter(BlogApply.apply_confirmation_id == apply_confirmation_id)
    # for name in names:
    #

    email_applys = ''.join(sessiondb.query(BlogPost.email).join(BlogApply).filter(BlogApply.apply_confirmation_id == apply_confirmation_id).first_or_404())


    # titles = sessiondb.query(BlogPost.title).join(BlogApply).filter(BlogApply.apply_confirmation_id == apply_confirmation_id).first_or_404()

    emails = ''.join(sessiondb.query(BlogApply.email_apply).filter(BlogApply.apply_confirmation_id == apply_confirmation_id).first_or_404())



    sendmailconnect(email_applys,emails,)
    return redirect (url_for('posts'))

def sendmailconnect(email_applys,emails):
    msg = Message('Hello', sender = 'handytest753@gmail.com', recipients = [emails])
    msg.body = f"Pleas contact {email_applys}"
    mail.send(msg)





























@app.route('/')
def index():
    return render_template('index.html')

#app.add_url_rule("/", None, view_func=index)

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

# jan naredil podstran
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

# jan naredil podstran
@app.route('/chmail', methods=['GET','POST'])
def chmail():
    return render_template('chmail.html')


#  jan naredil podstran za main post
# @app.route('/mainposts', methods=['GET', 'POST'])
# def mainposts():
#         # returns all posts query.order_by date_posted
#         all_posts = BlogPost.query.filter(BlogPost.confirmed == True).order_by(BlogPost.date_posted).all()
#         return render_template('mainposts.html', posts=all_posts)


# jan naredil podstran za main post
# @app.route('/editing/<int:id>', methods=['GET', 'POST'])
# def editing(id):
#      post = BlogPost.query.get_or_404(id)
# render_template('editing.html', )


@app.route('/editing/<int:id>', methods=['GET', 'POST'])
def editing(id):
        # returns all posts query.order_by date_posted
        post = BlogPost.query.filter(BlogPost.id == id)
        return render_template('editing.html', posts=post)
#       post = BlogPost.query.get_or_404(id)
#        id = BlogPost.query.filter(BlogPost.confirmed == True).all()




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