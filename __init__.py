from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/forum')
def forum():
    return render_template('forum.html')


if __name__ == '__main__':
    app.run()

