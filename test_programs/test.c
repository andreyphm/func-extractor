#include <stdio.h>
#include <stdlib.h>

double add(double a, double b)
{
    return a + b;
}

int add(int a, int b)
{
    return a + b;
}

static int sub(int a, int b)
{
    return a - b;
}

int* create_array(int size)
{
    int* array = (int*) calloc(size, sizeof(int));
    return array;
}

int factorial(int n)
{
    if (n <= 1)
    {
        return 1;
    }

    return n * factorial(n - 1);
}

int main()
{
    int sum = add(2, 3);
    printf("%d\n", factorial(sum));
}
