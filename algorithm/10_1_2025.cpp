#include <iostream>
using namespace std;
class Node{
    public:
    int data;
    Node* next;
    Node(){
        data = 0;
        next = NULL;

    }
    Node(int data){
        this->data = data;
        this->next = NULL;
    }
};
class Linkedlist {
    Node *head;
    public:
    Linkedlist(){
        head = NULL;
    }
    void push(int data){
        Node *newNode = new Node(data);
        if (head == NULL) {
            head = newNode;
            return;
        }
          newNode->next = this->head;
          this-> head = newNode;
    }
  void print(){
    Node *temp = head;
    if (head == NULL){
        cout << "List empty" << endl;
        return;
    }
    while (temp != NULL){
        cout << temp->data << " ";
        temp = temp->next;
    }
  }
  void ins_index(int data, int index){
    Node* temp = head;
    int currentIndex = 0;
    while (temp != NULL && currentIndex < index){
        temp = temp -> next;
        currentIndex++;
    }
    if (temp == NULL){
        cout << "Out of bound" << endl;
        return;
    }
    temp->data = data;
  }
  void deleteHead(){
    if(head == NULL){
        cout << "Invalid";
        
    }
    Node* temp = head;
    int value = temp -> data;
    head = head -> next;
    delete temp;
  }
  void deleteIndex(int index){
    if (index == 0){
        return deleteHead();
    }
    Node* temp = head;
    int currentIndex = 0;
    while (temp != NULL && currentIndex < index){
        temp = temp -> next;
        currentIndex++;
    }
    delete temp;
  }
  
};
int main(){
    Linkedlist list;
    list.push(4);
    list.push(3);
    list.push(2);
    list.push(1);
    cout << "Elements: ";
    list.print();
    cout << endl;
    return 0;
}