def reversed_enumerated(lst: list):
    length = len(lst)
    return ((length - 1 - i, lst[length - 1 - i]) for i in range(length))
