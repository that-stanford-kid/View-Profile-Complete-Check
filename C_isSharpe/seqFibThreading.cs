// In the FillArrayWithFunction, a lambda function is passed which calculates sum of the squares of the indices, which is more mathematical than incrementing. The PrintArray method abstracts away the logic & the array, making Main method clean.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System;

namespace SoloLearn
{
    class Program
    {
        static void Main(string[] args)
        {
            int[,,] arr = new int[3, 3, 3];
            FillArrayWithFunction(arr, (i, j, k) => i * i + j * j + k * k); // Using a lambda to define the function
            PrintArray(arr);

            Console.WriteLine("Rank: " + arr.Rank);
            Console.WriteLine("Length: " + arr.Length);
        }

        static void FillArrayWithFunction(int[,,] array, Func<int, int, int, int> function)
        {
            for (int i = 0; i < array.GetLength(0); i++)
            {
                for (int j = 0; j < array.GetLength(1); j++)
                {
                    for (int k = 0; k < array.GetLength(2); k++)
                    {
                        array[i, j, k] = function(i, j, k);
                    }
                }
            }
        }

        static void PrintArray(int[,,] array)
        {
            for (int i = 0; i < array.GetLength(0); i++)
            {
                for (int j = 0; j < array.GetLength(1); j++)
                {
                    for (int k = 0; k < array.GetLength(2); k++)
                    {
                        Console.Write($"{array[i, j, k]:D3} ");
                    }
                    Console.WriteLine();
                }
                Console.WriteLine();
            }
        }
    }
}
// The lambda (i, j, k) => i * i + j * j + k * k is a simple mathematical function that takes the indices of the array and calculates the sum of their squares, which could represent the evaluation of a mathematical function at each point in a three-dimensional space.
// This refactoring makes the code modular and introduces a bit more complexity by allowing  mathematical function used to fill the array without altering the loop structure.





