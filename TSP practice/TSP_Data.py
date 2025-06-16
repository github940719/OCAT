import random
import ast

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


def storeDistMatrix(n, distMatrix, path, optDist, optRoute, optTime):
    with open(path, "w") as f:
        f.write("the first, second, third, forth line is n, optDist, optRoute, optTime respectively\n")
        f.write("the remaining lines are the distMatrix\n")
        f.write(f"{n}\n")
        f.write(f"{optDist}\n")
        f.write(f"{optRoute}\n")
        f.write(f"{optTime}\n\n")
        for row in distMatrix:
            f.write(" ".join(map(str, row)) + "\n")


def readDistMatrix(path):
    with open(path, "r") as f:
        lines = f.readlines()
        n = int(lines[2].strip())
        optDist = float(lines[3].strip())
        optRoute = ast.literal_eval(lines[4].strip())
        optTime = float(lines[5].strip())
        distMatrix = []
        for line in lines[7:]:
            row = list(map(float, line.strip().split()))
            distMatrix.append(row)
    return n, distMatrix, optDist, optRoute, optTime
