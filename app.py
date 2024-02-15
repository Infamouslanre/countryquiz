from flask import Flask, render_template, request, session, redirect, url_for
import random
import requests
from unidecode import unidecode

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def remove_diacritics(text):
    return unidecode(text)

def get_random_question():
    # Fetch a random country
    country_data = requests.get('https://restcountries.com/v3.1/all').json()
    random_country = random.choice(country_data)

    # Get country name and capital
    country_name = random_country['name']['common']
    capital = random_country['capital'][0]

    return country_name, capital

@app.route('/')
def index():
    if 'question' not in session:
        session['question'] = get_random_question()

    country_name, capital = session['question']
    return render_template('index.html', country_name=country_name, capital=capital, attempts_left=session.get('attempts_left', 3))

@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_answer = request.form['answer']
    correct_answer = session['question'][1]
    attempts_left = session.get('attempts_left', 3)

    user_answer_cleaned = remove_diacritics(user_answer.lower())
    correct_answer_cleaned = remove_diacritics(correct_answer.lower())

    if user_answer_cleaned == correct_answer_cleaned:
        result = "Correct!"
    else:
        attempts_left -= 1
        if attempts_left > 0:
            result = f"Incorrect. You have {attempts_left} attempts left. Try again!"
        else:
            result = "Incorrect. You have no more attempts left. The correct answer is " + correct_answer

    session['attempts_left'] = attempts_left
    return render_template('result.html', result=result, attempts_left=attempts_left)

@app.route('/reset')
def reset():
    session.pop('question', None)
    session.pop('attempts_left', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
