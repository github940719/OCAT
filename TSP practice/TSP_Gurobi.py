from gurobipy import Model, GRB, quicksum
import time


statusDict = {
    GRB.OPTIMAL: "Optimal",
    GRB.INFEASIBLE: "Infeasible",
    GRB.UNBOUNDED: "Unbounded",
    GRB.TIME_LIMIT: "Time Limit",
    GRB.SUBOPTIMAL: "Suboptimal",
}


def Opt_TSP_MTZ(distMatrix, n):
    m = Model("TSP")

    # decision variables: x[i, j] and u[i] (to eliminate subtour)
    x = m.addVars(n, n, vtype = GRB.BINARY, name = "x")
    u = m.addVars(n, vtype = GRB.CONTINUOUS, name = "u")

    # objective: minimize total dist
    m.setObjective(quicksum(distMatrix[i][j] * x[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE)

    # constraints: leave and enter each node exactly once
    for i in range(n):
        m.addConstr(quicksum(x[i, j] for j in range(n)) == 1)
        m.addConstr(quicksum(x[j, i] for j in range(n)) == 1)

    # constraints: subtour elimination (MTZ)
    for i in range(1, n):
        for j in range(1, n):
            m.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)

    # optimize
    startTime = time.time()
    m.optimize()
    endTime = time.time()

    # extract the solution
    route = []
    if m.Status == GRB.OPTIMAL:
        current = 0
        route = [current]
        for _ in range(n):
            for j in range(n):
                if x[current, j].X > 0.5:
                    route.append(j)
                    current = j
                    break
        return statusDict.get(m.Status), m.ObjVal, route, endTime - startTime
    else:
        return statusDict.get(m.Status, default = f"Other: {m.Status}"), None, None, endTime - startTime
