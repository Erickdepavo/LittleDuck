echo "cycles.ld"
./little_duck.sh ./examples/cycles.ld

echo "\nconditions.ld"
./little_duck.sh ./examples/conditions.ld

echo "\ncircular_deps1.ld y circular_deps2.ld"
./little_duck.sh ./examples/circular_deps_1.ld -deps ./examples/circular_deps_2.ld

echo "\ncircular_deps1.ld y conditions.ld"
./little_duck.sh ./examples/circular_deps_1.ld -deps ./examples/conditions.ld

echo "\nfunction_never_returns.ld"
./little_duck.sh ./examples/function_never_returns.ld

echo "\nvar_test.ld"
./little_duck.sh ./examples/var_test.ld

echo "\ncode.ld"
./little_duck.sh code.ld -deps algorithms.ld

echo "\nalgorithms.ld"
./little_duck.sh algorithms.ld
