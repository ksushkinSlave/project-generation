

# Координаты точки в изометрической системе координат
def coords(x, y):
    return x - y, (x + y) / 2


# Координата X точки в изометрической системе координат
def x(x, y):
    return x - y


# Координата Y точки в изометрической системе координат
def y(x, y):
    return (x + y) / 2