using Godot;
using System;
using System.Collections.Generic;

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

            // while we do this, update the problem string
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

		// Now generate the wrong answers
		int rangeOfWrongAnswers = 10;

		wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, answer).ToString();
        wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, answer).ToString();
        wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, answer).ToString();

        return new Question(problem, answer.ToString(), wrong);
	}

	private static int GenerateWrongAnswer(int rangeOfWrongAnswers, int answer)
	{
		int randomNumber = 0;
		do
		{
			randomNumber = rand.Next(answer - rangeOfWrongAnswers / 2, answer + rangeOfWrongAnswers / 2);
		} while (randomNumber == answer);

		return randomNumber;
	}
}
