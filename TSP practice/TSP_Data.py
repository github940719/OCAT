import random
import matplotlib.pyplot as plt

def genCoords(n, seed = None, lb = 0, ub = 100):
    if seed is not None:
        random.seed(seed)
    coords = []
    for _ in range(n):
        coords.append((random.uniform(lb, ub), random.uniform(lb, ub)))
    return coords


def genDistMatrix(n, coords):
    distMatrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i+1, n):
            xj, yj = coords[j]
            dist = ( (xi - xj)**2 + (yi - yj)**2 )**0.5
            distMatrix[i][j] = dist
            distMatrix[j][i] = dist
    return distMatrix


def plotRoute(coords, route, color, legend):
    # draw the point
    for idx, (x, y) in enumerate(coords):
        plt.text(x, y, str(idx), color = "black", fontsize = 12)

    # draw the route
    routeX = [coords[i][0] for i in route]
    routeY = [coords[i][1] for i in route]
    plt.plot(routeX, routeY, color = color, linewidth = 2, label = legend)
    plt.legend()
    plt.title("TSP Route")
    plt.show()