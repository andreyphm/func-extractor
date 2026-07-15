import java.util.Arrays;

public class Calculator
{
    public int add(int a, int b)
    {
        return a + b;
    }

    private static int sub(int a, int b)
    {
        return a - b;
    }

    public int[] create_array(int size)
    {
        int[] array = new int[size];
        Arrays.fill(array, 0);
        return array;
    }

    public int factorial(int n)
    {
        if (n <= 1)
        {
            return 1;
        }

        return n * factorial(n - 1);
    }

    static class InnerHelper
    {
        int returnFunc42()
        {
            return return42();
        }

        private int return42()
        {
            return 42;
        }
    }

    public static void main(String[] args)
    {
        Calculator calc = new Calculator();
        int sum = calc.add(2, 3);
        System.out.println(calc.factorial(sum));
    }
}
