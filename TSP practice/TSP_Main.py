from TSP_Gurobi import Opt_TSP_MTZ
from TSP_Data import genCoords, genDistMatrix, plotRoute
from TSP_GA import GeneticAlgorithmTSP

nodeCnt = 50
coords = genCoords(nodeCnt)
distMatrix = genDistMatrix(nodeCnt, coords)

guboriStatus, optDist, optRoute, optTime = Opt_TSP_MTZ(distMatrix, nodeCnt)
print("\n-------------")
print("Gurobi")
print(f"dist = {optDist:.5f}")
print(f"tour = {optRoute}")
print(f"time = {optTime:.5f} sec")
# plotRoute(coords, optRoute, "red", "OPT")

GA = GeneticAlgorithmTSP(distMatrix, nodeCnt)
GAdist, GAroute, GAtime = GA.run()
print("\n-------------")
print("GA")
print(f"dist = {GAdist:.5f}, with gap = {(GAdist - optDist) / optDist:.2%}")
print(f"tour = {GAroute}")
print(f"time = {GAtime:.5f} sec")
# plotRoute(coords, GAroute, "blue", "GA")