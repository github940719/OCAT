import time
from UFLP_gurobi import gurobiOpt
from UFLP_tabu_track import TabuSearch
from dataGeneration import readData
import matplotlib.pyplot as plt

# parameter
maxStag = 5
tabuTenure = 5

count = 100
fixCost, distMatrix = readData(count, fixCostType = "medium", num = 3)


# gurobi
startGurobi = time.time()
gurobiScore, gurobiAssignment = gurobiOpt(fixCost, count, distMatrix)
endGurobi = time.time()
gurobiTime = endGurobi - startGurobi


# Tabu Search
startTabu = time.time()
tabu = TabuSearch(count, fixCost, distMatrix, tabuTenure)
tabuScore, tabuAssignment, history, flipCnt, swapCnt = tabu.main(maxStag, "medium", 0.1, seed = 10159719)
endTabu = time.time()
tabuTime = endTabu - startTabu
optimalGap = (tabuScore - gurobiScore) / gurobiScore

# print the optimal solution
print("\n------------------------------------")
print(f"optimal cost: {gurobiScore:.5f}")
print(f"Gurobi execution time (sec) = {gurobiTime:.10f}")

print("Tabu Search")
print(f"Best score: {tabuScore:.5f}")
print(f"Execution time (sec) = {tabuTime:.10f}")
print(f"Optimality Gap: {optimalGap:.2%}")
print("flip = ", flipCnt, "swap = ", swapCnt)

# compare the facility
diff = 0
gurobiFac = set()
tabuFac = set()

# compare the assignment
diff = 0
for i in range(count):
    if gurobiAssignment[i] != tabuAssignment[i]:
        diff += 1
    if gurobiAssignment[i] not in gurobiFac:
        gurobiFac.add(gurobiAssignment[i])
    if tabuAssignment[i] not in tabuFac:
        tabuFac.add(tabuAssignment[i])
print("gurobi", sorted(list(gurobiFac)))
print("tabu", sorted(list(tabuFac)))
print("diff =", diff)


# plot the tabu search progress
history = [score / 1000 for score in history]
plt.plot([i for i in range(len(history))], history, label = f"TS, {tabuTime:.5f} sec")
plt.plot([i for i in range(len(history))], [gurobiScore / 1000] * len(history), label = f"OPT, {gurobiTime:.5f} sec")
plt.xlabel('Iteration')
plt.ylabel('Best Score (thousand)')
plt.title('Tabu Search Progress')
plt.legend()
plt.show()