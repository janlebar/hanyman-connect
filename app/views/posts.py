# posts.py

from flask import render_template, request, url_for
# from .app import items  # Import app and items from app.py
from database import BlogPost  # Import the BlogPost model from database.py
from flask import Blueprint


posts_blueprint = Blueprint('posts', __name__)

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
