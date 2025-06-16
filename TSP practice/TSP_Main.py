from TSP_Gurobi import Opt_TSP_MTZ
from TSP_Data import genCoords, genDistMatrix, storeDistMatrix, readDistMatrix
from TSP_GA import GeneticAlgorithmTSP

# nodeCnt = 40
# coords = genCoords(nodeCnt)
# distMatrix = genDistMatrix(nodeCnt, coords)

# guboriStatus, optDist, optRoute, optTime = Opt_TSP_MTZ(distMatrix, nodeCnt)

path = "C:/Users/jaspe/Desktop/lecture/TSP practice/TSP dataset/"
path += ("file" + input("number: ") + ".txt")
nodeCnt, distMatrix, optDist, optRoute, optTime = readDistMatrix(path)

print("\n-------------")
print("Gurobi")
print(f"dist = {optDist:.5f}")
print(f"tour = {optRoute}")
print(f"time = {optTime:.5f} sec")

GA = GeneticAlgorithmTSP(distMatrix, nodeCnt, populationSize = 100, maxStag = 100, crossoverRate = 0.9, mutationRate = 0.05, eliteRate = 0.05)
GAdist, GAroute, GAtime = GA.run()
print("\n-------------")
print("GA")
print(f"dist = {GAdist:.5f}, with gap = {(GAdist - optDist) / optDist:.2%}")
print(f"tour = {GAroute}")
print(f"time = {GAtime:.5f} sec")


# if input("store y/n: ") == "y":
#     path = "C:/Users/jaspe/Desktop/lecture/TSP practice/TSP dataset/"
#     path += ("file" + input("number: ") + ".txt")
#     storeDistMatrix(nodeCnt, distMatrix, path, optDist, optRoute, optTime)
