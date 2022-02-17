from flask import Flask, render_template, request, flash, redirect
import os
from ML.model import make_predictions
from ML.field import make_calculations, calculate_field_area

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/process/', methods=['POST'])
def process():
    if not request.files:
        print('D: GOT EMPTY FILE LIST DURING POST REQUEST')
        return 'FAIL'

    # Split coordinates
    field_coords = []
    t = []
    for index, elem in enumerate(request.form['fieldCoords'].split(',')):
        t.append(int(elem))

        if index % 2 != 0:
            field_coords.append(t)
            t = []
    print(field_coords)
        

    # All files are stored in the dict as (PHOTO_NUMBER, FILE)
    # PHOTO_NUMBER -- int from 0 to n - 1
    create_dir_if_necessary('unprocessed_images')
    create_dir_if_necessary('results')

    files = request.files
    for i in range(len(request.files)):
        needed_file = request.files.get(str(i))
        needed_file.save('./static/unprocessed_images/' + needed_file.name + '.png')

    print('MAKING PREDICTIONS...')
    filed_lst = make_predictions('png', './static/unprocessed_images/', './static/results/')
    field_area = calculate_field_area(field_coords)
    total_wheat, density = make_calculations(filed_lst, field_area)
    # total_wheat = -1
    # density = -2
    # total_area = -3
    print(total_wheat, density)
    print('END PREDICT')

    return str(field_area) + ';' + str(total_wheat) + ';' + str(density)


def create_dir_if_necessary(dir_name):
    if os.path.exists('static/' + dir_name):
        print('EXISTS')
        return
    os.mkdir('static/' + dir_name)


if __name__ == '__main__':
    app.run(debug=True)
