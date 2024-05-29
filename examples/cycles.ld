program CyclesTest;
main {
    // While
    var i: int;
    i = 0;
    while (i < 5) {
        i = i + 1;
        print(i);
    }

    // Do while
    do {
        print(i);
    } while (i < 5);

    /*
    Should print:
    1
    2
    3
    4
    5
    5
    */
    return 0;
}
end;