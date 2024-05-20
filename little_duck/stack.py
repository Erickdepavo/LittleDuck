from collections import deque
from typing import Deque, Generic, Iterable, Iterator, TypeVar

# Define a type variable
T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self, items: Iterable[T] = []):
        # Initialize an empty deque
        self.container: Deque[T] = deque(items)
    
    def push(self, item: T) -> None:
        "Adds item to the top of the stack"
        self.container.append(item)
    
    def pop(self) -> T:
        "Removes and returns the top item of the stack"
        return self.container.pop()
    
    def top(self, offset: int = 0) -> T:
        "Returns the top item of the stack without removing it"
        return self.container[-1 - offset]
    
    def bottom(self, offset: int = 0) -> T:
        "Returns the bottom item of the stack without removing it"
        return self.container[0 + offset]
    
    def is_empty(self) -> bool:
        "Returns whether the stack is empty"
        return not self.container
    
    def size(self) -> int:
        "Returns the number of items in the stack"
        return len(self.container)
    
    def __iter__(self) -> Iterator[T]:
        # Return an iterator to allow iteration from top to bottom of the stack
        return reversed(self.container)
    
    def __str__(self) -> str:
        return f"Stack([{', '.join(map(str, self.container))}])"
    
    def __bool__(self) -> bool:
        return not self.is_empty()
    
    def __len__(self) -> int:
        return self.size()
