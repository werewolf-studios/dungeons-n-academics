using Godot;
using System;
using System.Collections.Generic;
using System.Linq;

public partial class QuestionConversionHandler : Node
{	
	private static Random rand = new Random();
	public static Question AdditionSubtractionConverter(QuestionFormat questionFormat)
	{
		string problem = questionFormat.ProblemFormat;
		string problemFormat = questionFormat.ProblemFormat;
		int min = int.Parse(questionFormat.Min);
        int max = int.Parse(questionFormat.Max);
        int answer = 0;
		string[] wrong = new string[3];

		// Determining how many underscores need to be replaced and where in the string they are at
        List<int> randomNumbers = new List<int>();
        int currentIndex = problem.IndexOf("_");

		while(currentIndex != -1)
		{
			// Generate a random number
			int randomNumber = rand.Next(min,max);
			randomNumbers.Add(randomNumber);

            // While we do this, update the problem string
            problem = problem.Remove(currentIndex, 1);
            problem = problem.Insert(currentIndex, randomNumber.ToString());

			currentIndex = problem.IndexOf("_");
		}

		// Now we move on to figuring out the answer
		// We need to get the symbols in the addition subtraction equation
		// We remove all spaces and underscores in the question format, which leaves all of the symbols
		problemFormat = problemFormat.Replace(" ", "");
		problemFormat = problemFormat.Replace("_", "");

		// Based on the specific code, we can solve the answer
		switch (problemFormat)
		{
			case "+=X":
				answer = (randomNumbers[0] + randomNumbers[1]);
				break;
			case "-=X":
                answer = (randomNumbers[0] - randomNumbers[1]);
                break;
			case "X+=":
                answer = (randomNumbers[1] - randomNumbers[0]);
                break;
			case "X-=":
                answer = (randomNumbers[0] + randomNumbers[1]);
                break;
			case "++=X":
				answer = (randomNumbers[0] + randomNumbers[1] + randomNumbers[2]);
				break;
			case "--=X":
                // This is a special case because it almost always results in a negative number
                // So we will recalculate the random numbers right here

                // This will always result in a non negative number because the first number is always larger than the other two numbers combined
                randomNumbers[0] = rand.Next(500, 700);
				randomNumbers[1] = rand.Next(100, 250);
				randomNumbers[2] = rand.Next(100, 250);

				problem = $"{randomNumbers[0]} - {randomNumbers[1]} - {randomNumbers[2]} = X";

                answer = (randomNumbers[0] - randomNumbers[1] - randomNumbers[2]);
                break;
			case "+-=X":
                answer = (randomNumbers[0] + randomNumbers[1] - randomNumbers[2]);
                break;
			case "-+=X":
                answer = (randomNumbers[0] - randomNumbers[1] + randomNumbers[2]);
                break;
			default:
				throw new Exception("SYMBOL CODE NOT FOUND");
		}

		if(answer < 0)
		{
			GD.Print("REROLLING ANSWER CUZ IT WAS NEGATIVE");
			return AdditionSubtractionConverter(questionFormat);
        }

		// Now generate the wrong answers
		int rangeOfWrongAnswers = 10;
		int[] existingOptions = new int[3];
		existingOptions[0] = answer;

        wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions).ToString();
		existingOptions[1] = int.Parse(wrong[0]);
        wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions).ToString();
		existingOptions[2] = int.Parse(wrong[1]);
        wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions).ToString();

        return new Question(problem, answer.ToString(), wrong);
	}

	private static int GenerateWrongAnswer(int rangeOfWrongAnswers, int answer, int[] existingOptions)
	{
		int randomNumber = 0;
		do
		{
			randomNumber = rand.Next(answer - rangeOfWrongAnswers / 2, answer + rangeOfWrongAnswers / 2);
			// Make sure its not one of the other options and is not negative
		} while (existingOptions.Contains<int>(randomNumber) || randomNumber < 0);

		return randomNumber;
	}
}
