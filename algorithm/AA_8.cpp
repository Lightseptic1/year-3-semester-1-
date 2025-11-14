#include <iostream>
#include <stdexcept>
using namespace std;
class Node {
public:
    int data;
    int priority;
    Node* next;
    Node(int data, int priority) {
        this-> data = data;
        this-> priority = priority;
        this-> next = nullptr;
    }
};

class PriorityQueue {
private:
    Node* head;
public: 
 PriorityQueue(){
        head = nullptr;
    }

    void enqueu(int data, int priority) {

        Node* newNode = new Node (data, priority); 
        if (isEmpty() || priority > head->priority){
            newNode -> next = head;
            head = newNode;
            return;
        }
        Node* current = head;
        while (current->next != nullptr && current->next->priority >= priority){
            current = current-> next;
        }
        newNode->next = current->next;
        current->next = newNode;
    }

    int dequeue() {
        if (isEmpty()) {
            throw runtime_error("priority queue is empty");

        }
        int data = head->data;
        Node* temp = head;
        head = head->next;
        delete temp; 
        return data;
    }
    int peek(){
    if(isEmpty()){
        throw runtime_error("priority queue is emtpy");

    }
    return head -> data;

}
bool isEmpty(){
    return head == nullptr;
}
int size(){
    int count = 0;
    Node* current = head;
    while (current != nullptr){
        count++;
        current = current -> next;
    }
    return count;
}

void viewElements(){
    if (isEmpty()){
        cout << "Priorirt queue is empty" << endl;
        return;
    }
    Node* current = head;
    cout << "Elements (data, priorirty): " << endl;
    while (current != nullptr){
        cout << "(" << current -> data << ", " << current -> priority << ")" << endl;
        current = current -> next;
    }
}
void Clear_All() {
    while (head != nullptr) {
        Node* tmp = head;
        head = head->next;
        delete tmp;
    }
    head = nullptr;
}
};
int main (){
    PriorityQueue pq;
    pq.enqueu(10,2);
    pq.enqueu(5,1);
    pq.enqueu(15,3);

    cout << pq.size() << endl;
    cout << pq.peek() << endl;
    cout << pq.dequeue() << endl;
    cout << pq.size() << endl;
}