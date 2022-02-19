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
    for index, elem in enumerate(request.form['mapContour'].split(',')):
        t.append(int(elem))

        if index % 2 != 0:
            field_coords.append(t)
            t = []
    # print(field_coords)
    
    img_heights = {}
    for i in request.form:
        if i.endswith('.png'):
            img_heights[i] = int(request.form[i].split(',')[2])
        

    # All files are stored in the dict as (PHOTO_NUMBER, FILE)
    # PHOTO_NUMBER -- int from 0 to n - 1
    create_dir_if_necessary('unprocessed_images')
    create_dir_if_necessary('results')

    files = request.files
    for i in request.files:
        needed_file = request.files.get(i)
        needed_file.save('./static/unprocessed_images/' + i)

    print('MAKING PREDICTIONS...')

    filed_lst = make_predictions('./static/unprocessed_images/', './static/results/', img_heights)
    print('END PREDICT')
    field_area = calculate_field_area(field_coords)
    total_wheat, density = make_calculations(filed_lst, field_area)

    print(total_wheat, density)

    return str(field_area) + ';' + str(total_wheat) + ';' + str(density)


def create_dir_if_necessary(dir_name):
    if os.path.exists('static/' + dir_name):
        return
    os.mkdir('static/' + dir_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
