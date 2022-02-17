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