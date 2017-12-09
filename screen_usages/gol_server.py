from flask import Flask

from runners.gol_runner import GameOfLifeRunner

app = Flask(__name__)


@app.route("/")
def hello():
    return "Welcome to game of life!"


@app.route("/gol/<gol_input>")
def gol(gol_input):
    GameOfLifeRunner.create(gol_input, 50).start()
    return "Welcome to game of life! got input: " + gol_input


if __name__ == '__main__':
    app.run()  # don't do that, use FLASK_APP env
