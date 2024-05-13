from collections import deque
from typing import Deque, Generic, Iterator, TypeVar

# Define a type variable
T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self):
        # Initialize an empty deque
        self.container: Deque[T] = deque()
    
    def push(self, item: T) -> None:
        # Add item to the top of the stack
        self.container.append(item)
    
    def pop(self) -> T:
        # Remove and return the top item of the stack
        if self.is_empty():
            raise IndexError("pop from an empty stack")
        return self.container.pop()
    
    def top(self) -> T:
        # Return the top item of the stack without removing it
        if self.is_empty():
            raise IndexError("top from an empty stack")
        return self.container[-1]
    
    def bottom(self) -> T:
        # Return the bottom item of the stack without removing it
        if self.is_empty():
            raise IndexError("bottom from an empty stack")
        return self.container[0]
    
    def is_empty(self) -> bool:
        # Return True if the stack is empty, else False
        return not self.container
    
    def size(self) -> int:
        # Return the number of items in the stack
        return len(self.container)
    
    def __iter__(self) -> Iterator[T]:
        # Return an iterator to allow iteration from top to bottom of the stack
        return reversed(self.container)
