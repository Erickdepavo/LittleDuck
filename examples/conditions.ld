program ConditionsTest;
main {
    // If
    var i: int;
    i = 0;
    if (i < 5) {
        i = i + 1;
        print(i);
    }

    // If else
    if (true && !false) {
        print(4);
    } else {
        print(5);
    }

    /*
    Should print:
    1
    4
    */
    return 0;
}
end;