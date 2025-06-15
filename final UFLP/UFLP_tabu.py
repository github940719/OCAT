import random

class TabuSearch:

    def __init__(self, count, fixCost, distMatrix, tabuTenure):
        # input parameter
        self.fixCost = fixCost
        self.distMatrix = distMatrix
        self.tenure = tabuTenure
        self.count = count

        # sortedFacs[i] is the list of fac in descending order of dist from demand i
        self.sortedFacs = [] 
        for i in range(self.count):
            self.sortedFacs.append(sorted(range(self.count), key = lambda j: self.distMatrix[i][j]))

        # maintain the second best opened facility for each demand
        self.secondBestFac = [None for _ in range(self.count)]

        # current sol
        self.facs = [0] * self.count     # facs[j] = state of fac j (0 closed 1 open)
        self.assign = [None for _ in range(self.count)]  # assign[i] = demand i's assigned fac
        self.cost = 0

        # best neighbor
        self.bestNeighFlip = None
        self.bestNeighAssign = None
        self.bestNeighCost = float("inf")
        
        self.bestCost = float("inf")
        self.bestAssign = None
        self.tabu = [-tabuTenure] * self.count  # tabu[j] = step if last time we modify facility[j] is step


    def selfKmeans(self, k, seed):
        random.seed(seed)
        selected = [random.randint(0, self.count - 1)]
        notSelected = set(range(self.count))
        notSelected.remove(selected[0])
        self.facs[selected[0]] = 1  # random an initial facility
        self.cost += self.fixCost[selected[0]]

        for _ in range(1, k):  # we need to random k-1 more facilities
            dists = []
            candidates = list(notSelected)
            for f in candidates:
                minDist = min(self.distMatrix[f][s] for s in selected)
                dists.append(minDist ** 2)  # the minDist from existing fac ** 2

            # set the prob by dist (positively correlated)
            total = sum(dists)
            probs = [d / total for d in dists]

            # randomly choose nextFac by probs
            nextFac = random.choices(candidates, weights = probs, k = 1)[0]
            self.facs[nextFac] = 1
            self.cost += self.fixCost[nextFac]
            selected.append(nextFac)
            notSelected.remove(nextFac)


    def initialSolKmeans(self, initialRatio, seed):
        self.selfKmeans(k = int(self.count * initialRatio), seed = seed)  # this would modify self.facs and fixCost
        for i in range(self.count):
            for f in self.sortedFacs[i]:
                if self.facs[f]:  
                    if self.assign[i] is None:  # assign to the nearst open fac
                        self.assign[i] = f
                        self.cost += self.distMatrix[i][f]
                    else:
                        self.secondBestFac[i] = f
                        break

        self.bestCost = self.cost
        self.bestAssign = self.assign[:]


    def initialSolHighFix(self):
        # scores = fixCost + transportaion cost (assume all assigned to this fac)
        minScore = float("inf")
        fac = 0
        for f in range(self.count):
            score = self.fixCost[f] + sum(self.distMatrix[i][f] for i in range(self.count))
            if score < minScore:
                fac = f 
                minScore = score
        
        self.cost = minScore
        self.facs[fac] = 1
        self.assign = [fac for _ in range(self.count)]


    def findBestNeigh(self, forbidThreshold):
        self.bestNeighCost = float("inf")
        for j in range(self.count):  # neighbor type I: flip a fac at a time
            neighAssign = self.assign[:]

            if self.facs[j] == 0:  # open fac j
                self.facs[j] = 1
                neighCost = self.cost + self.openFacCostChange(neighAssign, j)
            else:  # close fac j
                self.facs[j] = 0
                neighCost = self.cost + self.closeFacCostChange(neighAssign, j)

            # tabu condition (forebidThreshold = iter - tenure) or aspiration rule
            forbid = self.tabu[j] >= forbidThreshold
            self.updateBestNeigh(neighCost, neighAssign, forbid, j)

            # neighbor type II : swap (open j and close k)
            if self.facs[j] == 0:
                self.facs[j] = 1
                continue

            for k in range(self.count):
                if self.facs[k] == 0 or k == j:
                    continue 

                self.facs[k] = 0  # close facility k
                swapAssign = neighAssign[:]
                swapCost = neighCost + self.closeFacCostChange(swapAssign, k, swapJustOpen = j)

                # forbid only when j, k are both in tabu!
                swapForbid = (forbid and self.tabu[k] >= forbidThreshold)
                self.updateBestNeigh(swapCost, swapAssign, swapForbid, (k, j))
                self.facs[k] = 1  # reset fac k to open

            # reset facs
            self.facs[j] = 0


    # openFacCostChange would nodify tempAssign
    def openFacCostChange(self, tempAssign, flipIndex):
        costAdd = self.fixCost[flipIndex]
        for i in range(self.count):
            diff = self.distMatrix[i][tempAssign[i]] - self.distMatrix[i][flipIndex]
            if diff > 0:  # reassign demand i to the new facility if dist is smaller
                tempAssign[i] = flipIndex
                costAdd -= diff
        return costAdd
    

    # closeFacCostChange would modify tempAssign
    def closeFacCostChange(self, tempAssign, flipIndex, swapJustOpen = None):
        if sum(self.facs) == 0:
            return float("inf")  # no opened facility

        costAdd = (-self.fixCost[flipIndex])
        for i in range(self.count):
            if tempAssign[i] != flipIndex:
                continue
            
            # demand i is originally assigned to the fac we want to close
            newFac = self.secondBestFac[i] 
            if newFac is None:
                newFac = swapJustOpen
            elif swapJustOpen and self.distMatrix[i][swapJustOpen] < self.distMatrix[i][newFac]:
                newFac = swapJustOpen

            tempAssign[i] = newFac  # reassign to the second best open facility
            costAdd += (self.distMatrix[i][newFac] - self.distMatrix[i][flipIndex]) 
    
        return costAdd
    
    
    def updateBestNeigh(self, neighCost, neighAssign, forbid, flip):
        general = not forbid and neighCost < self.bestNeighCost
        aspiration = forbid and neighCost < self.bestCost
        if general or aspiration:
            self.bestNeighAssign = neighAssign[:]
            self.bestNeighCost = neighCost
            self.bestNeighFlip = flip


    def renewSecondBest(self):
        for i in range(self.count):
            self.secondBestFac[i] = None
            for f in self.sortedFacs[i]:  # from close to far
                if self.facs[f] and f != self.assign[i]:
                    self.secondBestFac[i] = f
                    break


    def main(self, maxStag, fixCostType, initialRatio, seed):
        if fixCostType == "high":
            self.initialSolHighFix()
        else:
            self.initialSolKmeans(initialRatio, seed)
        iter = 0
        stag = 0

        # for record
        history = [self.bestCost]
        flipCnt = 0
        swapCnt = 0

        while stag < maxStag:
            iter += 1
            self.findBestNeigh(forbidThreshold = iter - self.tenure)

            # renew incumbent and stag
            if self.bestNeighCost < self.bestCost:
                self.bestCost = self.bestNeighCost
                self.bestAssign = self.bestNeighAssign[:]
                stag = 0  # reset stagnation
            else:
                stag += 1
            
            # reset current sol to this bestNeigh
            if isinstance(self.bestNeighFlip, int):  # flip is applied
                flipCnt += 1
                self.facs[self.bestNeighFlip] = 1 - self.facs[self.bestNeighFlip]
                self.tabu[self.bestNeighFlip] = iter
            else:  # swap is applied
                swapCnt += 1
                for f in self.bestNeighFlip:
                    self.facs[f] = 1 - self.facs[f]
                    self.tabu[f] = iter

            self.cost = self.bestNeighCost
            self.assign = self.bestNeighAssign[:]
            self.renewSecondBest()
            history.append(self.bestCost)

        return self.bestCost, self.bestAssign, history, flipCnt, swapCnt