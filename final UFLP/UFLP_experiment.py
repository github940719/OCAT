import time
import random
import pandas as pd
from UFLP_gurobi import gurobiOpt
from UFLP_tabu import TabuSearch
from dataGeneration import readData

# experiment parameter
count = 100
fixCostTypes = ["low", "medium", "high"]
nums = range(1, 11)
tabuTenures = [0, 1, 5, 10, 20]
maxStags = [1, 5, 10, 20]
initialSolRatio = 0.1
repeat = 10

results = []
expRemain = len(nums) * len(fixCostTypes) * len(tabuTenures) * len(maxStags)

# set the random seed
seeds = [random.randint(0, int(1e6)) for _ in range(repeat)]

for fixCostType in fixCostTypes:
    for num in nums:
        fixCost, distMatrix = readData(count, fixCostType, num)

        # Gurobi
        startGurobi = time.time()
        gurobiScore, gurobiAssignment = gurobiOpt(fixCost, count, distMatrix)
        endGurobi = time.time()
        gurobiTime = endGurobi - startGurobi

        for tabuTenure in tabuTenures:
            for maxStag in maxStags:

                if fixCostType == "high":
                    initialRatio = None
                else:
                    initialRatio = initialSolRatio
                    
                tabuScores = []
                tabuTimes = []
                flipCnts = []
                swapCnts = []

                for _ in range(repeat):  # "repeat" experiments on the same data

                    # Tabu Search
                    startTabu = time.time()
                    tabu = TabuSearch(count, fixCost, distMatrix, tabuTenure)
                    tabuScore, tabuAssignment, history, flipCnt, swapCnt = tabu.main(maxStag, fixCostType, initialRatio, seeds[_])
                    endTabu = time.time()
                    tabuTime = endTabu - startTabu

                    # the result
                    tabuScores.append(tabuScore)
                    tabuTimes.append(tabuTime)
                    flipCnts.append(flipCnt)
                    swapCnts.append(swapCnt)

                # average on the "repeat" results (since random initial sol)
                avgTabuScore = sum(tabuScores) / repeat
                avgTabuTime = sum(tabuTimes) / repeat
                avgFlipCnt = sum(flipCnts) / repeat
                avgSwapCnt = sum(swapCnts) / repeat
                totalIterations = avgFlipCnt + avgSwapCnt
                optimalGap = (avgTabuScore - gurobiScore) / gurobiScore

                # store the result to data frame
                results.append({
                    "fixCostType": fixCostType,
                    "num": num,
                    "tabuTenure": tabuTenure,
                    "maxStag": maxStag,
                    "gurobiTime": gurobiTime,
                    "avgTabuTime": avgTabuTime,
                    "optimalGap": optimalGap,
                    "avgFlipCnt": avgFlipCnt,
                    "avgSwapCnt": avgSwapCnt,
                    "totalIterations": totalIterations
                })

                expRemain -= 1
                print("fixCost", fixCostType, "tenure", tabuTenure, "maxStag", maxStag, "gap", round(optimalGap, 10), "remain", expRemain)


# average on the 30 testCases
df = pd.DataFrame(results)
df_grouped = df.groupby(["fixCostType", "tabuTenure", "maxStag"]).agg({
    "gurobiTime": "mean",
    "avgTabuTime": "mean",
    "optimalGap": "mean",
    "avgFlipCnt": "mean",
    "avgSwapCnt": "mean",
    "totalIterations": "mean"
}).reset_index()

# store the result to excel
df.to_excel("results.xlsx", index = False)
df_grouped.to_excel("results_grouped.xlsx", index = False)