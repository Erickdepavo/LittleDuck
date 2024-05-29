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
    x = 5;

    var fib_count: int;
    fib_count = 3;

    print("Factorial de", x, ":", factorial(x));
    print("Fibonacci:");

    var i: int;
    i = 0;
    do {
        print(fibonacci(i));
        i = i + 1;
    } while (i < fib_count + 1);

    return 0;
}
end;
