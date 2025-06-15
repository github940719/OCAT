from gurobipy import *

def gurobiOpt(fixCost, count, distMatrix):
    model = Model("UFLP")

    # Decision variables
    x = model.addVars(count, count, vtype = GRB.BINARY)
    y = model.addVars(count, vtype = GRB.BINARY)

    # Objective: minimize fixed cost + transportation cost
    model.setObjective(
        quicksum(fixCost[j] * y[j] for j in range(len(fixCost))) +
        quicksum(distMatrix[i][j] * x[i,j] for i in range(count) for j in range(count)),
        GRB.MINIMIZE)

    # Constraint 1: each customer is assigned to exactly one facility
    for i in range(count):
        model.addConstr(quicksum(x[i,j] for j in range(count)) == 1)

    # Constraint 2: if yi = 0, then x[i, j] = 0
    for j in range(count):
        for i in range(count):
            model.addConstr(x[i,j] <= y[j])

    # solve
    model.optimize()

    # answer
    assignment = []
    for i in range(count):
        for j in range(count):
            if x[i, j].X > 0.5:
                assignment.append(j)
                break
            
    return model.ObjVal, assignment