program ValidTest;

var x : int;
var y, z : float;

void function1(id : int) :
{
    x = id * 2;
}

float function2(id : float) :
{
    return (id + 3.14);
}

main {
    x = 10;
    y = 5.0;
    z = x + y;
    function1(x);
    print(x, y);
    if (x != y) {
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
