from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename

from os import system

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        if not request.files:
            return redirect(request.url)

        imgs_file = request.files.get('img')
        map_file = request.files.get('map')

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if imgs_file.filename == '':  # TODO: ADD POP-UP
            return redirect(request.url)

        print(request.files)
        print(imgs_file, map_file)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
