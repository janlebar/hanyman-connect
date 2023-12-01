# SWEARING PREWENTION
swear_words = []  # Global variable to store the loaded list of swear words

@app.before_first_request
def load_swear_words():
    global swear_words
    with open('swear_words.txt', 'r') as file:
        swear_words = [word.strip() for word in file.readlines()]