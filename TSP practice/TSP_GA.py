import random
import heapq
import time

class GeneticAlgorithmTSP:
    
    def __init__(self, distMatrix, nodeCnt, populationSize = 100, maxStag = 200, crossoverRate = 0.9, mutationRate = 0.05, eliteRate = 0.05):
        # data
        self.distMatrix = distMatrix
        self.nodeCnt = nodeCnt

        # parameter
        self.populationSize = populationSize
        self.maxStag = maxStag
        self.crossoverRate = crossoverRate
        self.mutationRate = mutationRate
        self.eliteRate = eliteRate

        # record
        self.stag = 0
        self.population = []
        self.fitnessList = []
        self.bestRoute = None
        self.bestDist = float("inf")


    def renew(self):
        # find the min fitness of all populations
        currentBestDist = float("inf")
        currentBestIdx = None
        self.fitnessList = []
        for idx, route in enumerate(self.population):
            tempDist = self.evaluateFitness(route)
            self.fitnessList.append(tempDist)
            if tempDist < currentBestDist:
                currentBestDist = tempDist
                currentBestIdx = idx

        # check whether currentBest is better than incumbent
        if currentBestDist < self.bestDist:
            self.stag = 0
            self.bestDist = currentBestDist
            self.bestRoute = self.population[currentBestIdx][:]
        else:
            self.stag += 1


    def run(self):
        startTime = time.time()
        self.initializePopulation()
        self.renew()

        while self.stag < self.maxStag:

            # elite preservation
            newPopulation = self.selectElite()

            # crossover to generate the remaining offspring
            while len(newPopulation) < self.populationSize:
                parent1 = self.wheelSelection()
                parent2 = self.wheelSelection()

                # crossover or not, depending on the crossoverRate
                if random.random() < self.crossoverRate:
                    offspring1, offspring2 = self.crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1[:], parent2[:]  # remain

                # mutate or not, depending on the mutateRate
                if random.random() < self.mutationRate:
                    self.mutate(offspring1)
                if random.random() < self.mutationRate:
                    self.mutate(offspring2)

                newPopulation += [offspring1, offspring2]

            self.population = newPopulation[:self.populationSize]
            self.renew()

        endTime = time.time()
        return self.bestDist, self.bestRoute + [self.bestRoute[0]], endTime - startTime


    def initializePopulation(self):
        base = list(range(self.nodeCnt))
        for _ in range(self.populationSize):
            route = base[:]
            random.shuffle(route)  # shuffle [0, 1, ..., n]
            self.population.append(route)


    def evaluateFitness(self, route):
        totalDist = 0
        for i in range(self.nodeCnt-1):
            fromNode = route[i]
            toNode = route[i+1]
            totalDist += self.distMatrix[fromNode][toNode]
        return totalDist + self.distMatrix[route[-1]][route[0]]  # back to the depot
    

    # preserve "eliteCnt" elites
    def selectElite(self):
        elitesIdx = heapq.nsmallest(int(self.nodeCnt * self.eliteRate), range(self.populationSize), 
            key = lambda idx: self.fitnessList[idx])
        return [self.population[i][:] for i in elitesIdx]


    def wheelSelection(self):
        # the smaller the dist, the largest the weight
        fitnessScores = [1.0 / dist for dist in self.fitnessList]  
        selected = random.choices(self.population, weights = fitnessScores, k = 1)[0]
        return selected


    # partially mapped crossover
    def crossover(self, parent1, parent2):
        size = self.nodeCnt

        # choose a segment to remain as parent
        cxPoint1, cxPoint2 = sorted(random.sample(range(size), 2))
        offspring1 = [None] * size
        offspring2 = [None] * size
        offspring1[cxPoint1:cxPoint2] = parent1[cxPoint1:cxPoint2]
        offspring2[cxPoint1:cxPoint2] = parent2[cxPoint1:cxPoint2]

        #  to prevent visiting a node twice or no visiting
        def pmxFill(offspring, donor, cxPoint1, cxPoint2):
            """ basic idea:
                if node G (iddex = 5) in the donor segment also appears in the offspring segment : no problem
                if not, then when we copy the remaining part of donor to offspring: G will be skipped
                so, we obtain the idx of offspring[5] in donor,
                if offspring[idx] is empty, then we write donor[idx] here
                if not, keep searing.
            """

            # build the donor value -> index dict to speed up searching
            donorPos = {val: idx for idx, val in enumerate(donor)}

            for i in range(cxPoint1, cxPoint2):  # first check the segment
                if donor[i] in offspring:
                    continue
                    
                # donor[i] is not in the offspring, we should add it somewhere
                pos = i
                while True:
                    pos = donorPos[offspring[pos]]
                    if offspring[pos] is None:
                        offspring[pos] = donor[i]
                        break

            # second, copy the remaining part of the donor to the offspring
            for i in range(size):
                if offspring[i] is None:
                    offspring[i] = donor[i]
        
        pmxFill(offspring1, parent2, cxPoint1, cxPoint2)
        pmxFill(offspring2, parent1, cxPoint1, cxPoint2)
        return offspring1, offspring2


    # mutate: randomly select one method
    def mutate(self, route):
        n = self.nodeCnt
        op = random.choice(["swap", "reverse", "insert", "scramble"])

        if op == "swap":  # swap two nodes
            i, j = random.sample(range(n), 2)
            route[i], route[j] = route[j], route[i]

        elif op == "reverse":  # reverse a segment
            i, j = sorted(random.sample(range(n), 2))
            route[i:j+1] = reversed(route[i:j+1])

        elif op == "insert":  # city in idx = i to idx = j
            i, j = random.sample(range(n), 2)
            city = route.pop(i)
            route.insert(j, city)

        elif op == "scramble":  # shuffle a segment
            i, j = sorted(random.sample(range(n), 2))
            subset = route[i:j+1]
            random.shuffle(subset)
            route[i:j+1] = subset