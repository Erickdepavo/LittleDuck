program ValidTest;

var x : int;
var y, z : float;

// Comment
void function1(id : int) :
{
    x = id * 2;
    var test: string;
    test = "Hola Mundo!";
    print(test);
}

/*
    Block comment
*/
void function2(id : float) :
{
    print (id + 3.14);
}

/* Inline block comment */
main {
    x = 10;
    y = 5.0;
    z = x + y;
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
}
end;
