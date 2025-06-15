import random

path = "C:/Users/jaspe/Desktop/課程/運輸最佳化/group final/randomData/"


def randomGeneration(count, fixCostType, num):
    # distMatrix
    distMatrix = [[0 for _ in range(count)] for _ in range(count)]
    for i in range(count):
        for j in range(i, count):
            distMatrix[i][j] = random.randint(1000, 2000)
            distMatrix[j][i] = distMatrix[i][j]
                
    # fixCost
    fixCostrange = (100, 200)
    if fixCostType == "medium":
        fixCostrange = (1000, 2000)
    elif fixCostType == "high":
        fixCostrange = (10000, 20000)

    fixCost = []
    for f in range(count):
        fixCost.append(random.randint(fixCostrange[0], fixCostrange[1]))
    
    # store the data
    fileName = "count" + str(count) + "_" + str(fixCostType) + "Cost_" + str(num)
    with open(path + fileName + ".txt", "w") as file:
        # the first line is fixCost
        file.write(" ".join(map(str, fixCost)) + "\n")
        # the second to the last line is the distMatrix
        for row in distMatrix:
            file.write(" ".join(map(str, row)) + "\n")


def readData(count, fixCostType, num):
    fixCost = []
    distMatrix = []
    fileName = "count" + str(count) + "_" + str(fixCostType) + "Cost_" + str(num)
    
    # Read the file
    with open(path + fileName + ".txt", "r") as file:
        lines = file.readlines()
        
        # First line: fixCost
        fixCost = list(map(int, lines[0].strip().split()))
        
        # Remaining lines: distMatrix
        for line in lines[1:]:
            distMatrix.append(list(map(int, line.strip().split())))
    
    return fixCost, distMatrix


if __name__ == "__main__":
    for count in [100]:
        for fixCostType in ["low", "medium", "high"]:
            for num in range(10):  # each type, we generate 30 testCase
                randomGeneration(count, fixCostType, num+1)
                print(count, fixCostType, num+1)