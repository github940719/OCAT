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
    // Load data
    ifstream infile("C:\\Users\\jaspe\\Desktop\\課程\\運輸最佳化\\duo assignment\\PDPTW dataset\\LC1_2_5.txt");
    int vehicleCnt, capacity, speed;
    infile >> vehicleCnt >> capacity >> speed;
    vehicleCnt = 20; // Adjust if needed

    int index, x, y, q, e, l, s, p, d;
    vector<int> x_coord, y_coord, quantity, earliest, latest, service, d_of_p;
    while (infile >> index >> x >> y >> q >> e >> l >> s >> p >> d) {
        x_coord.push_back(x);
        y_coord.push_back(y);
        quantity.push_back(q);
        earliest.push_back(e);
        latest.push_back(l);
        service.push_back(s);
        d_of_p.push_back(d); // d_of_p[i] = delivery node of pickup i
    }

    // Add depot as the last node
    x_coord.push_back(x_coord[0]);
    y_coord.push_back(y_coord[0]);
    quantity.push_back(quantity[0]);
    earliest.push_back(earliest[0]);
    latest.push_back(latest[0]);
    service.push_back(service[0]);
    d_of_p.push_back(d_of_p[0]);

    int totalNodeCnt = x_coord.size(); // 2n+2

    try {
        GRBEnv env;
        GRBModel model(env);

        // Variables
        vector<vector<vector<GRBVar>>> x(totalNodeCnt, vector<vector<GRBVar>>(totalNodeCnt, vector<GRBVar>(vehicleCnt)));
        vector<vector<GRBVar>> B(totalNodeCnt, vector<GRBVar>(vehicleCnt));
        vector<vector<GRBVar>> Q(totalNodeCnt, vector<GRBVar>(vehicleCnt));

        for (int i = 0; i < totalNodeCnt; i++) {
            for (int j = 0; j < totalNodeCnt; j++) {
                for (int k = 0; k < vehicleCnt; k++) {
                    x[i][j][k] = model.addVar(0.0, 1.0, 0.0, GRB_BINARY);
                }
            }
        }

        for (int i = 0; i < totalNodeCnt; i++) {
            for (int k = 0; k < vehicleCnt; k++) {
                B[i][k] = model.addVar(earliest[i], latest[i], 0.0, GRB_CONTINUOUS);
                Q[i][k] = model.addVar(0.0, capacity, 0.0, GRB_CONTINUOUS);
            }
        }

        // Objective: Minimize total distance
        GRBLinExpr obj = 0;
        for (int i = 0; i < totalNodeCnt; i++) {
            for (int j = 0; j < totalNodeCnt; j++) {
                for (int k = 0; k < vehicleCnt; k++) {
                    double dist = calculateDistance(x_coord[i], y_coord[i], x_coord[j], y_coord[j]);
                    obj += dist * x[i][j][k];
                }
            }
        }
        model.setObjective(obj, GRB_MINIMIZE);

        // Constraints
        // 2. outflow for pickup node
        for (int i = 1; i < totalNodeCnt - 1; i++) {
            if (quantity[i] > 0) {  // for all i <- P
                GRBLinExpr sum = 0;
                for (int j = 0; j < totalNodeCnt; j++) {
                    for (int k = 0; k < vehicleCnt; k++) {
                        sum += x[i][j][k];
                    }
                }
                model.addConstr(sum == 1);
            }
        }

        // 3. pick up and delivery by the same vehicle (delivery outflow is guaranteed automatically)
        for (int i = 1; i < totalNodeCnt - 1; i++) {
            if (quantity[i] > 0) {  // for all i <- P
                for (int k = 0; k < vehicleCnt; k++) {  // for all vehicle
                    GRBLinExpr sum1 = 0, sum2 = 0;
                    for (int j = 0; j < totalNodeCnt; j++) {
                        sum1 += x[i][j][k];
                        sum2 += x[d_of_p[i]][j][k];
                    }
                    model.addConstr(sum1 - sum2 == 0);
                }
            }
        }

        // 4. depot outflow
        for (int k = 0; k < vehicleCnt; k++) {
            GRBLinExpr sum = 0;
            for (int j = 1; j < totalNodeCnt - 1; j++) {
                sum += x[0][j][k];
            }
            model.addConstr(sum == 1);
        }

        // 5. depot inflow
        for (int k = 0; k < vehicleCnt; k++) {
            GRBLinExpr sum = 0;
            for (int i = 1; i < totalNodeCnt - 1; i++) {
                sum += x[i][totalNodeCnt - 1][k];
            }
            model.addConstr(sum == 1);
        }

        // 6. for all node i, inflow and outflow by the same vehicle (inflow is guaranteed automatically)
        for (int i = 1; i < totalNodeCnt - 1; i++) {  // for all i <- P union D
            for (int k = 0; k < vehicleCnt; k++) {  // for all vehicle
                GRBLinExpr sum1 = 0;
                GRBLinExpr sum2 = 0;
                for (int j = 0; j < totalNodeCnt; j++) {
                    sum1 += x[j][i][k];
                    sum2 += x[i][j][k];
                }
                model.addConstr(sum1 - sum2 == 0);
            }
        }

        // 7. cummulative arrival time
        // 8. cummulative load
        for (int i = 0; i < totalNodeCnt; i++) {  // for all i <- N
            for (int j = 0; j < totalNodeCnt; j++) {  // for all j <- N
                for (int k = 0; k < vehicleCnt; k++) {  // for all vehicle
                    double dist = calculateDistance(x_coord[i], y_coord[i], x_coord[j], y_coord[j]);
                    // double M = latest[i] - earliest[j] + dist;
                    double M = latest[i] - earliest[j] + dist + service[i];
                    model.addConstr(B[j][k] >= B[i][k] + service[i] + dist - M * (1 - x[i][j][k]));

                    M = capacity + quantity[j];
                    model.addConstr(Q[j][k] >= Q[i][k] + quantity[j] - M * (1 - x[i][j][k]));
                }
            }
        }

        // 9. pick up before delivery
        for (int i = 1; i < totalNodeCnt - 1; i++) {
            if (quantity[i] > 0) {  // for all i <- P
                for (int k = 0; k < vehicleCnt; k++) {  // for all vehicle
                    model.addConstr(B[d_of_p[i]][k] >= B[i][k] + service[i] + calculateDistance(x_coord[i], y_coord[i], x_coord[d_of_p[i]], y_coord[d_of_p[i]]));
                }
            }
        }

        // 10. time window : has been set
        // 11. total load
        for (int k = 0; k < vehicleCnt; k++) {  // for all vehicle
            for (int i = 0; i < totalNodeCnt; i++) {  // for all i <- N
                model.addConstr(Q[i][k] <= min(capacity, capacity + quantity[i]));
                model.addConstr(max(0, quantity[i]) <= Q[i][k]);
            }
        }

        // Solve
        clock_t start = clock();
        model.optimize();
        clock_t end = clock();

        // Output
        if (model.get(GRB_IntAttr_Status) == GRB_OPTIMAL) {
            cout << "\n-------------------------\n";
            cout << "execution time (sec) = " << double(end - start) / CLOCKS_PER_SEC << endl;
            cout << "Optimal cost: " << model.get(GRB_DoubleAttr_ObjVal) << endl;
            for (int k = 0; k < vehicleCnt; k++) {
                cout << "Vehicle " << k << ": ";
                int current = 0; // Start at depot
                while (current != totalNodeCnt - 1) {
                    for (int j = 0; j < totalNodeCnt; j++) {
                        if (x[current][j][k].get(GRB_DoubleAttr_X) > 0.5) {
                            if (current != 0) cout << current << " ";
                            current = j;
                            break;
                        }
                    }
                }
                cout << endl;
            }
        }
        else {
            cout << "No optimal solution found." << endl;
        }
    }
    catch (GRBException& e) {
        cerr << "Gurobi error: " << e.getMessage() << endl;
    }
    catch (...) {
        cerr << "Unknown error" << endl;
    }

    return 0;
}
