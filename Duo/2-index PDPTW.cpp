#include <iostream>
#include <vector>
#include <fstream>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include "gurobi_c++.h"
using namespace std;


double calculateDistance(int x1, int y1, int x2, int y2) {
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
}

int main() {

    // load the parameter
    ifstream infile("C:\\Users\\jaspe\\Desktop\\課程\\運輸最佳化\\duo assignment\\PDPTW dataset\\LC1_2_5.txt");

    int vehicleCnt, capacity, speed;
    infile >> vehicleCnt >> capacity >> speed;  // speed = 1, so dist = travel time
    vehicleCnt = 20;

    int index, x, y, q, e, l, s, p, d;
    vector<int> x_coord, y_coord, quantity, earliest, latest, service, d_of_p;
    while (infile >> index >> x >> y >> q >> e >> l >> s >> p >> d) {  // we would not use p
        x_coord.push_back(x);
        y_coord.push_back(y);
        quantity.push_back(q);
        earliest.push_back(e);
        latest.push_back(l);
        service.push_back(s);
        d_of_p.push_back(d);  // d_of_p[i] = j if j is the delivery node of i
    }

    // add the depot to the last node
    x_coord.push_back(x_coord[0]);
    y_coord.push_back(y_coord[0]);
    quantity.push_back(quantity[0]);
    earliest.push_back(earliest[0]);
    latest.push_back(latest[0]);
    service.push_back(service[0]);
    d_of_p.push_back(d_of_p[0]);

    int totalNodeCnt = x_coord.size();


    try {
        // Initialize Gurobi environment and model
        GRBEnv env = GRBEnv();
        GRBModel model = GRBModel(env);


        // Decision variables (stored in vector)
        // x[i][j] = 1 if a vehicle travels from node i to node j
        vector<vector<GRBVar>> x(totalNodeCnt, vector<GRBVar>(totalNodeCnt));
        for (int i = 0; i < totalNodeCnt; i++) {
            for (int j = 0; j < totalNodeCnt; j++) {
                x[i][j] = model.addVar(0.0, 1.0, 0.0, GRB_BINARY);
                // lower bound, upper bound, initial value, type
            }
        }


        // B[i] = arrival time of vehicle at node i
        vector<GRBVar> B(totalNodeCnt);
        for (int i = 0; i < totalNodeCnt; i++) {
            B[i] = model.addVar(earliest[i], latest[i], 0.0, GRB_CONTINUOUS);  // time window
        }

        // Q[i] = loaded quantity of vehicle at node i
        vector<GRBVar> Q(totalNodeCnt);
        for (int i = 0; i < totalNodeCnt; i++) {
            Q[i] = model.addVar(0.0, capacity, 0.0, GRB_CONTINUOUS);
        }

        // v[i] = the first node of the route that node i belongs to
        vector<GRBVar> v(totalNodeCnt);
        for (int i = 0; i < totalNodeCnt; i++) {
            v[i] = model.addVar(0.0, totalNodeCnt, 0.0, GRB_CONTINUOUS);
        }


        // object function : min total distance (cost) -(1)
        GRBLinExpr obj = 0;
        for (int i = 0; i < totalNodeCnt - 1; i++) {  // impossible to depart from totalNodeCnt - 1
            for (int j = 1; j < totalNodeCnt; j++) {  // impossible to arrive at 0
                double dist = calculateDistance(x_coord[i], y_coord[i], x_coord[j], y_coord[j]);
                obj += dist * x[i][j];
            }
        }
        model.setObjective(obj, GRB_MINIMIZE);


        // constraints (2) : inflow
        for (int j = 1; j < totalNodeCnt; j++) {  // for all j <- P union D [union the depot]
            GRBLinExpr sum = 0;
            for (int i = 0; i < totalNodeCnt; i++) {
                sum += x[i][j];
            }

            if (j == totalNodeCnt - 1) {  // for the depot
                model.addConstr(sum == vehicleCnt);
            }
            else {
                model.addConstr(sum == 1);
            }
        }

        // constraints (3) : outflow
        for (int i = 0; i < totalNodeCnt - 1; i++) {  // for all i <- P union D [union the depot]
            GRBLinExpr sum = 0;
            for (int j = 0; j < totalNodeCnt; j++) {
                sum += x[i][j];
            }

            if (i == 0) {  // for the depot
                model.addConstr(sum == vehicleCnt);
            }
            else {
                model.addConstr(sum == 1);
            }
        }


        // constraints (4), (5) : arrival time and load change
        for (int i = 0; i < totalNodeCnt; i++) {  // for all i <- N
            for (int j = 0; j < totalNodeCnt; j++) {  // for all j <- N
                double dist = calculateDistance(x_coord[i], y_coord[i], x_coord[j], y_coord[j]);
                // double M = latest[i] - earliest[j] + dist;
                double M = latest[i] - earliest[j] + dist + service[i];
                model.addConstr(B[j] >= B[i] + service[i] + dist - M * (1 - x[i][j]));

                M = capacity + quantity[j];
                model.addConstr(Q[j] >= Q[i] + quantity[j] - M * (1 - x[i][j]));
            }
        }

        // constraints (6) : time window (ei <= Bi <= li has been set)

        // constraints (7) : total load
        for (int i = 0; i < totalNodeCnt; i++) {  // for all i <- N
            model.addConstr(Q[i] <= min(capacity, capacity + quantity[i]));
            model.addConstr(max(0, quantity[i]) <= Q[i]);
        }

        // constraints (8) : pick-up before delivery
        for (int i = 1; i < totalNodeCnt - 1; i++) { // for all i <- P
            if (quantity[i] > 0) {  // this is the pick-up node
                model.addConstr(B[d_of_p[i]] >= B[i] +
                    calculateDistance(x_coord[i], y_coord[i], x_coord[d_of_p[i]], y_coord[d_of_p[i]]));
            }
        }

        // constraints (9) : pick-up and delivery node are traveled by the same vehicle
        for (int i = 1; i < totalNodeCnt - 1; i++) {  // for all i <- P
            if (quantity[i] > 0) {  // this is the pick-up node
                model.addConstr(v[i] == v[d_of_p[i]]);
            }
        }

        // constraints (10), (11) : vj = j if j is the first node of the route
        for (int j = 1; j < totalNodeCnt - 1; j++) {  // for all i <- P union D
            model.addConstr(v[j] >= j * x[0][j]);
            model.addConstr(v[j] <= j * x[0][j] - totalNodeCnt * (x[0][j] - 1));
        }

        // constraints (12), (13) : if xij = 0, then vi = vj
        for (int i = 1; i < totalNodeCnt - 1; i++) {  // for all i <- P union D
            for (int j = 1; j < totalNodeCnt - 1; j++) {  // for all j <- P union D
                model.addConstr(v[j] >= v[i] + totalNodeCnt * (x[i][j] - 1));
                model.addConstr(v[j] <= v[i] + totalNodeCnt * (1 - x[i][j]));
            }
        }

        // trivial fixation
        for (int i = 1; i < totalNodeCnt - 1; i++) {   // for all i <- P union D
            model.addConstr(x[i][i] == 0);
            model.addConstr(x[i][0] == 0);
            model.addConstr(x[totalNodeCnt - 1][i] == 0);

            if (quantity[i] > 0) {  // for all i <- P
                model.addConstr(x[i][totalNodeCnt - 1] == 0);
                model.addConstr(x[d_of_p[i]][i] == 0);
            }

            if (quantity[i] < 0) {  // for all i <- D
                model.addConstr(x[0][i] == 0);
            }

            for (int j = 1; j < totalNodeCnt - 1; j++) {  // for all i, j <- P union D

                if (earliest[i] + service[i] + calculateDistance(x_coord[i], y_coord[i], x_coord[j], y_coord[j]) > latest[j]) {
                    model.addConstr(x[i][j] == 0);
                }

                if (quantity[i] > 0 && quantity[j] > 0 && quantity[i] + quantity[j] > capacity) {  // for all i, j <- P
                    model.addConstr(x[i][j] == 0);
                    model.addConstr(x[i][d_of_p[j]] == 0);
                    model.addConstr(x[d_of_p[i]][d_of_p[j]] == 0);
                }
            }
        }


        // optimize the model
        clock_t start = clock();
        model.optimize();
		clock_t end = clock();

        // output the result
        if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL) {
            cout << "\n------------------------------\n";
            cout << "execution time (sec) = " << double(end - start) / CLOCKS_PER_SEC << endl;
            cout << "optimal (minimized) cost: " << model.get(GRB_DoubleAttr_ObjVal);

            for (int i = 1; i < totalNodeCnt - 1; i++) {
                if (x[0][i].get(GRB_DoubleAttr_X) < 0.5) {
                    continue;
                }

                // node i is the starting node of the route
                cout << endl << "Route : ";
                for (int j = i; j != totalNodeCnt - 1;) {
                    cout << j << " ";
                    for (int k = 1; k < totalNodeCnt; k++) {
                        if (x[j][k].get(GRB_DoubleAttr_X) > 0.5) {  // travel from j to k
                            j = k;
                            break;
                        }
                    }
                }
            }
            cout << "\n------------------------------\n";
        }
        else {
            cout << "No optimal solution found." << endl;
        }
    }
    catch (GRBException e) {
        cout << "Gurobi Error code: " << e.getErrorCode() << endl;
        cout << e.getMessage() << endl;
    }

    return 0;
}
