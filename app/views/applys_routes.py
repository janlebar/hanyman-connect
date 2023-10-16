from flask import render_template, request, url_for
# from .app import items  # Import app and items from app.py
from app.models.database import BlogPost  # Import the BlogPost model from database.py
from flask import Blueprint, current_app
from app.constants.constants import items
from flask_mail import Mail
from flask_mail import Message
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, flash, session
from secrets import randbelow

applys_blueprint = Blueprint('applys', __name__)


@applys_blueprint.route('/apply/new/<id>', methods=['GET', 'POST'])
def new_apply(id):
    return render_template('new_apply.html', blog_post_id=id, action_url=url_for('applys.new_apply',id=id))
