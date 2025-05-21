# views/utilities_routes.py
from flask import Flask, Blueprint,current_app


utilities_blueprint = Blueprint('utilities', __name__)

# SWEARING PREWENTION
swear_words = []  # Global variable to store the loaded list of swear words

@utilities_blueprint.before_app_first_request
def load_swear_words():
    global swear_words
    with open('swear_words.txt', 'r') as file:
        swear_words = [word.strip() for word in file.readlines()]