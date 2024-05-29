program ValidTest;

var x : int;
var y, z : float;

// Comment
void function1(id : int) : 
{
    // Comment
    x = id * 2;
    var test: string;
    test = "Hola Mundo!";
    print(test, x);
    return;
}

/*
    Block comment
*/
void function2(n : float, m: int) :
{
    print (n + 3.14, m);
    return;
}

/* Inline block comment */
main {
    x = 10;
    y = 5.0;
    z = x + -y;
    var new: bool;
    new = true;
    function1(x);
    print(x, y);
    if (x == y) {
        print(x);
    } else {
        print(y);
    }
    do {
        print(x);
        x = x - 1;
    } while (x != 0);
    var test: float;
    test = 9 + 45.0 * 35 / (2 + -3);
    if (false && !false || -0) {
        print("Funciona");
    }
    return 0;
}
end;
