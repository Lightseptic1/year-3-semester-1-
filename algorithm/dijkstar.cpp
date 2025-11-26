#include <iostream>
#include <climits> // For INT_MAX
using namespace std;

#define V 5 // Number of vertices in the graph

// Function to find the vertex with the minimum distance value
int findMinDistance(int dist[], bool sptSet[]) {
    int min = INT_MAX, minIndex = -1;

    for (int v = 0; v < V; v++) {
        if (!sptSet[v] && dist[v] < min) { // Vertex not in the shortest path tree and has a smaller distance
           min = dist[v];
           minIndex = v;

        }
    }
    return minIndex;
}

// Function to print the shortest path distances from the source
void printSolution(int dist[]) {
    cout << "Vertex\tDistance from Source\n";
    for (int i = 0; i < V; i++) {
        cout << i << "\t" << dist[i] << "\n";
    }
}

// Function to implement Dijkstra's Algorithm
void dijkstra(int graph[V][V], int src) {
    int dist[V];     // Distance array to store the shortest distances
    bool sptSet[V];  // sptSet[i] will be true if vertex i is included in the shortest path tree

    // Initialize distances to infinity and sptSet to false
    for (int i = 0; i < V; i++) {
      dist[i] = INT_MAX;
      sptSet[i] = false;
    }

    dist[src] = 0; // Distance of the source vertex to itself is always 0

    // Loop to find the shortest path for all vertices
    for (int count = 0; count < V - 1; count++) {
        // Pick the minimum distance vertex from the set of vertices not yet processed
        int u = findMinDistance(dist, sptSet);

        // Include the picked vertex in the shortest path tree
        sptSet[u] = true;

        // Update the distances of adjacent vertices of the picked vertex
        for (int v = 0; v < V; v++) {
            // Update dist[v] if:
            // 1. There is an edge from u to v.
            // 2. v is not in sptSet.
            // 3. The total weight of the path through u is smaller than dist[v].
            if (!sptSet[v] && graph[u][v] && dist[u] != INT_MAX && dist[u] + graph[u][v] < dist[v]) {
              dist[v] = dist[u] + graph[u][v];
            }
        }
    }

    // Print the shortest path distances
    printSolution(dist);
}

int main() {
    // Example graph represented as an adjacency matrix
    int graph[V][V] = {
        {0, 10, 0, 0, 5},
        {0, 0, 1, 0, 2},
        {0, 0, 0, 4, 0},
        {7, 0, 6, 0, 0},
        {0, 3, 9, 2, 0}
    };

    int src = 0; // Source vertex
    dijkstra(graph, src);

    return 0;
}