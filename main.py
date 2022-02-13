from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename

from os import system

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/process/', methods=['POST'])
def process():
    if not request.files:
        print('D: EMPTY FILE LIST IN POST REQUEST')
        return redirect(request.url)

    print(request.files)
    files = request.files
    for i in files:
        files[i].save(files[i].name + '.png')
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
