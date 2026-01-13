# dsa_structures.py
from collections import deque
import heapq

# DOUBLY LINKED LIST
# Used for Cart items management
class DLLNode:
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    # Insert at the end (O(1))
    def append(self, value):
        node = DLLNode(value)
        if not self.head:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1

    # Remove first matching value (O(n))
    def remove_first_value(self, value):
        current = self.head
        while current:
            if current.value == value:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev

                self.size -= 1
                return True
            current = current.next
        return False

    # Traverse list
    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

    def __len__(self):
        return self.size

    def __iter__(self):
        current = self.head
        while current:
            yield current.value
            current = current.next

# STACK (LIFO)
# Used for UNDO operations
class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if not self._data:
            return None
        return self._data.pop()

    def __len__(self):
        return len(self._data)

# QUEUE (FIFO)
# Used for NORMAL borrow requests
class Queue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, item):
        self._queue.append(item)

    def dequeue(self):
        if not self._queue:
            return None
        return self._queue.popleft()

    def __len__(self):
        return len(self._queue)

# PRIORITY QUEUE (Min-Heap)
# Used for PRIORITIZED borrowing
class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0  # preserves FIFO among same priority

    def push(self, priority, item):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[2]

    def __len__(self):
        return len(self._heap)
