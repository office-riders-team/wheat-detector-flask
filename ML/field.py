from matplotlib import pyplot as plt
from matplotlib import pylab


def calculate_field_area(corners):
    """
    Формула площади Гаусса
    """
    n = len(corners)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area


def create_points_plot(coords, photos, f_lst):
    """
    Визуализация поля и точек фотографии
    """
    size = [(i[1])**1.5 for i in f_lst]

    x, y = [cord[0] for cord in coords], [cord[1] for cord in coords]
    p_x, p_y = [p[0] for p in photos], [p[1] for p in photos]
    x.append(coords[0][0])
    y.append(coords[0][1])

    plt.rcParams["figure.figsize"] = (8, 6)
    ax = plt.axes()
    fig = pylab.gcf()
    fig.canvas.manager.set_window_title('Поле')

    plt.plot(x, y, '-o', label='Контур', c='#08D9D6')
    ax.fill(x, y, c='#08D9D6', alpha=0.1, zorder=1)

    plt.scatter(p_x, p_y, c='#FF2E63', label='Фотографии', s=size, zorder=2)

    plt.legend()
    plt.title('Поле')

    plt.show()


def make_calculations(f_lst, field_area):
    total_density = sum([t[3] for t in f_lst]) / len(f_lst)
    total_wheat = field_area * total_density

    return round(total_wheat, 5), round(total_density, 5)


def get_coords(path):
    try:
        coords = []
        with open(path, 'r') as file:
            for line in file.readlines():
                coords.append(tuple([int(i) for i in line.rstrip().split()]))
        return coords
    except:
        raise