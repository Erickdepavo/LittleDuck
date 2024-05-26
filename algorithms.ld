program Algorithms;

/*
    Recursive implementation of Factorial
*/
int factorial(n: int) :
{
    if (n == 0) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

// Recursive implementation of Fibonacci
int fibonacci(n: int) :
{   
    if (n == 0 || n < 0) {
        return 0;
    // Change to else if when supported
    } else {
        if (n == 1) {
            return 1;
        } else {
            return fibonacci(n - 1) + fibonacci(n - 2);
        }
    }
}

main {
    var x: int;
    x = 10; // Maybe add input here?
    print("X:", x);
    print("Factorial:", factorial(x));
    print("Fibonacci:", fibonacci(x));
}
end;
