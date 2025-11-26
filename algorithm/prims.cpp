#include <iostream>
#include <climits> // For INT_MAX
using namespace std;

// Function to find the vertex with the minimum key value that is not yet included in the MST
int findMinKeyVertex(int key[], bool mstSet[], int V) {
    int minKey = INT_MAX, minIndex = -1;

    for (int v = 0; v < V; v++) {
        if (!mstSet[v] && key[v] < minKey) {
        minKey = key[v];
        minIndex = v;
        }
    }
    return minIndex;
}

// Function to print the MST
void printMST(int parent[], int graph[5][5], int V) {
    cout << "Edge\tWeight\n";
    for (int i = 1; i < V; i++) {
        cout << parent[i] << " - " << i << "\t" << graph[i][parent[i]] << "\n";
    }
}

// Function to implement Prim's Algorithm
void primMST(int graph[5][5], int V) {
    int key[V];         // To store the minimum weight edge for each vertex
    bool mstSet[V];     // To keep track of vertices included in the MST
    int parent[V];      // To store the MST

    // Initialize all keys to a large value (infinity) and mstSet to false
    for (int i = 0; i < V; i++) {
        key[i] = INT_MAX;
        mstSet[i] = false;
    }

    // Start with the first vertex
    ----------       // Make the first vertex's key 0 so that it is picked first
    ----------     // The first vertex is the root of the MST
    key[0] = 0;

    parent[0] = -1;
    for (int count = 0; count < V - 1; count++) {
        // Pick the vertex with the minimum key value that is not yet included in the MST
        int u = findMinKeyVertex(key, mstSet, V);

        // Include the picked vertex in the MST
        mstSet[u] = true;

        // Update the key and parent index of adjacent vertices
        for (int v = 0; v < V; v++) {
            // Update key[v] if:
            // 1. There is an edge from u to v.
            // 2. v is not in mstSet.
            // 3. The weight of the edge (u, v) is smaller than key[v].
            if (graph[u][v] && !mstSet[v] && graph[u][v] < key[v]) {
                parent[v] = u;
                key[v] = graph[u][v];
            }
        }
    }

    // Print the MST
    printMST(parent, graph, V);
}

int main() {
    // Example graph represented as an adjacency matrix
    int graph[5][5] = {
        {0, 2, 0, 6, 0},
        {2, 0, 3, 8, 5},
        {0, 3, 0, 0, 7},
        {6, 8, 0, 0, 9},
        {0, 5, 7, 9, 0}
    };

    int V = 5; // Number of vertices
    primMST(graph, V);

    return 0;
}