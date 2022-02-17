from flask import Flask, render_template, request, flash, redirect
from ML.model import make_predictions

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/process/', methods=['POST'])
def process():
    if not request.files:
        print('D: GOT EMPTY FILE LIST DURING POST REQUEST')
        return redirect(request.url)

    # All files are stored in the dict as (PHOTO_NUMBER, FILE)
    # PHOTO_NUMBER -- int from 0 to n - 1
    files = request.files
    for i in range(len(request.files)):
        needed_file = request.files.get(str(i))
        needed_file.save('./static/unprocessed_images/' + needed_file.name + '.png')

    print('MAKING PREDICTIONS...')
    make_predictions('png', './static/unprocessed_images/', './static/results/')
    print('END PREDICT')

    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
