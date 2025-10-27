# Sorting Algorithms Reference

quick notes for reference

---

### Bubble Sort
- goes through the list multiple times  
- compares each pair of items  
- swaps them if out of order  
- keeps doing this until no swaps left  

**complexity:**  
- best: O(n)  
- average: O(n²)  
- worst: O(n²)  
- space: O(1)

---

### Insertion Sort
- builds the sorted list one element at a time  
- takes each new element and inserts it into the correct spot among the previous ones  

**complexity:**  
- best: O(n)  
- average: O(n²)  
- worst: O(n²)  
- space: O(1)

---

### Selection Sort
- divides the list into sorted and unsorted parts  
- repeatedly finds the smallest element from the unsorted portion  
- swaps it with the first unsorted element  
- continues until all elements are sorted  

**complexity:**  
- best: O(n²)  
- average: O(n²)  
- worst: O(n²)  
- space: O(1)

**notes:**  
- makes fewer swaps than bubble sort  
- not stable (order of equal elements may change)  
- simple but inefficient for large lists  

---

### Quick Sort
- divide and conquer algorithm  
- selects a **pivot** element  
- partitions array so smaller elements go left, larger ones go right  
- recursively sorts the left and right sides  

**complexity:**  
- best: O(n log n)  
- average: O(n log n)  
- worst: O(n²) *(when pivot choice is poor)*  
- space: O(log n) (for recursion stack)

**notes:**  
- much faster on average than bubble/selection/insertion  
- can be implemented **in-place** (no extra array needed)  
- choice of pivot strongly affects performance  
- not stable by default  

---

> **Summary:**  
> - Bubble/Insertion/Selection → simple but slow (O(n²))  
> - Quick Sort → fast on average, divide-and-conquer (O(n log n))
