from flask import render_template, request, url_for
# from .app import items  # Import app and items from app.py
from app.models.database import BlogPost  # Import the BlogPost model from database.py
# from flask import Blueprint, current_app

posts_blueprint = Blueprint('posts', __name__)

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


@app.route('/post/<string:id>', methods=['GET', 'POST'])
def post(id):
    # returns all posts query.order_by date_posted

    all_posts = BlogPost.query.filter(BlogPost.id == id)

    urls = {post.id: post.id
        for post in all_posts}
    return render_template('posts.html', posts=all_posts, urls=urls)       

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    print(items)
    # categories = Category.query.all()
    return render_template('new_post.html', items=items, action_url=url_for(posts.__name__))

@app.route('/save_post', methods=['POST'])
def save_post():
    # if spodi ipolne form oz ga prebere
    # POST /posts

    post_title = request.form['title']
    post_content = request.form['content']
    post_offer = request.form['offer']
    post_email = request.form['email']
    post_longitude = request.form['longitude']
    post_latitude = request.form['latitude']
    post_item = request.form['item']  
    post_confirmation_id = randbelow(2 ** 31)
    post_phonenumber = request.form['phonenumber']
    # session['email'] = post_email

    for word in swear_words:
        if word[:4].lower() in post_title.lower():
                 return render_template('swearingnotallowed.html')

    new_post = BlogPost(title=post_title,content=post_content,offer=post_offer,longitude=post_longitude,latitude=post_latitude,email=post_email,
    confirmation_id=post_confirmation_id,category=post_item,phonenumber=post_phonenumber)

    # vpise v bazo v trenutno
    db.session.add(new_post)
    # commit ga sele vpise permanentno v bazo
    db.session.commit()
    
    print("Latitude:", post_latitude)
    print("Longitude:", post_longitude)


    # poklical funkcijo sendmail in jo izpolnil z parametri iz posts
    sendmail(post_email, post_confirmation_id)


    try:
        sendmail(post_email, post_confirmation_id)
        flash('', "info")
    except Exception as e:
        flash("An error occurred while sending the email.", "error")
        # Handle the error, maybe log it or display an error message
    # vrne posodobljen posts page
    return redirect('/posts')


# posts mail function
def sendmail(email, confirmation_id):
    msg = Message('Confirm your post', sender='handytest753@gmail.com', recipients=[email])
    # msg.body = f"Click to confirm {BASE_URL}/posts/confirm/{confirmation_id}"
    confirmation_url = url_for("confirm", id=confirmation_id, _external=True)
    
    msg.html = render_template(
        'email_template.html',
        confirmation_url=confirmation_url
    )
    mail.send(msg)

    try:
        with current_app.app_context():
            mail.send(msg)
        return True
    except Exception as e:
        print(e)
        flash("Something went wrong while sending the email.")  # Flash this message on email sending failure
        return redirect('/posts')  # Redirect to a suitable page after failure






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
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.offer = request.form['offer']
        post.content = request.form['content']
        post.email = request.form['email']
        post.phonenumber = request.form['phonenumber']
        post.category = request.form['category']  # Change 'item' to 'category'
        db.session.commit()
        return redirect('/posts')
    else:
        # post=post ker rabi prebrisat prejsn povst
        # post_item = post.category  # Assign the current category value
        return render_template('edit.html', post=post,items=items)

# POSTS WITH TIME LIMIT

@app.route('/posttimelimit', methods=['GET'])
def posttimelimit():
    # calculate the date from one month ago
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    # query for posts from the last month
    all_posts = BlogPost.query.filter(BlogPost.date_posted >= one_month_ago).all()
    # urls, dictionary, for all posts id that were queried above transformed with serializer
    urls = {post.id: post.id for post in all_posts}
    return render_template('posts.html', posts=all_posts, urls=urls)