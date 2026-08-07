using Godot;
using System;
using System.Collections.Generic;
using System.ComponentModel.Design.Serialization;
using System.Linq;

public partial class QuestionConversionHandler : Node
{
	private const string QUESTION_KEY = "?";
	private static Random rand = new Random();

    public static Question ConvertIntoQuestion(QuestionFormat questionFormat, Topic topic)
    {
        if(topic == Topic.AdditionAndSubtraction)
        {
            return AdditionSubtractionConverter(questionFormat);
        }

        if(topic == Topic.Multiplication || topic == Topic.Division)
        {
            return MultiplicationAndDivisionConverter(questionFormat);
        }

        if(topic == Topic.Geometry)
        {
            return GeometryConverter(questionFormat);
        }

        // Add more topics as needed
        throw new ArgumentException("Unsupported Conversion for " + topic.ToString());
    }
	private static Question AdditionSubtractionConverter(QuestionFormat questionFormat)
	{
		// Get data from the question format
		string problem = questionFormat.ProblemFormat;
		string problemFormat = questionFormat.ProblemFormat;
		int min = int.Parse(questionFormat.Min);
        int max = int.Parse(questionFormat.Max);
        int answer = 0;
		string[] wrong = new string[3];

		// Some error checks here
		ErrorChecks(problem,min,max);

		// Determining how many underscores need to be replaced and where in the string they are at
        List<int> randomNumbers = new List<int>();

		problem = GetUnderscores(randomNumbers, problem, min, max);

        // Now we move on to figuring out the answer
        // We need to get the symbols in the addition subtraction equation
        // We remove all spaces and underscores in the question format, which leaves all of the symbols
        problemFormat = problemFormat.Replace(" ", "");
		problemFormat = problemFormat.Replace("_", "");

		// Based on the specific code, we can solve the answer
		switch (problemFormat)
		{
			case $"+={QUESTION_KEY}":
				answer = (randomNumbers[0] + randomNumbers[1]);
				break;
			case $"-={QUESTION_KEY}":
                answer = (randomNumbers[0] - randomNumbers[1]);
                break;
			case $"{QUESTION_KEY}+=":
                answer = (randomNumbers[1] - randomNumbers[0]);
                break;
			case $"{QUESTION_KEY}-=":
                answer = (randomNumbers[0] + randomNumbers[1]);
                break;
			case $"++={QUESTION_KEY}":
				answer = (randomNumbers[0] + randomNumbers[1] + randomNumbers[2]);
				break;
			case $"--={QUESTION_KEY}":
                // This is a special case because it almost always results in a negative number
                // So we will recalculate the random numbers right here

                // This will always result in a non negative number because the first number is always larger than the other two numbers combined
                randomNumbers[0] = rand.Next(500, 700);
				randomNumbers[1] = rand.Next(100, 250);
				randomNumbers[2] = rand.Next(100, 250);

				problem = $"{randomNumbers[0]} - {randomNumbers[1]} - {randomNumbers[2]} = {QUESTION_KEY}";

                answer = (randomNumbers[0] - randomNumbers[1] - randomNumbers[2]);
                break;
			case $"+-={QUESTION_KEY}":
                answer = (randomNumbers[0] + randomNumbers[1] - randomNumbers[2]);
                break;
			case $"-+={QUESTION_KEY}":
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

        wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false).ToString();
		existingOptions[1] = int.Parse(wrong[0]);
        wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false).ToString();
		existingOptions[2] = int.Parse(wrong[1]);
        wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false).ToString();

        return new Question(problem, answer.ToString(), wrong);
	}

    private static Question MultiplicationAndDivisionConverter(QuestionFormat questionFormat)
	{
        // Get data from the question format
        string problem = questionFormat.ProblemFormat;
        string problemFormat = questionFormat.ProblemFormat;
        int min = int.Parse(questionFormat.Min);
        int max = int.Parse(questionFormat.Max);
        int quotient = 0;
        string[] wrong = new string[3];

        // Some error checks here
        ErrorChecks(problem, min, max);

        // Determining how many underscores need to be replaced and where in the string they are at
        List<int> randomNumbers = new List<int>();

        problem = GetUnderscores(randomNumbers, problem, min, max);

        // Now we move on to figuring out the answer
        // We need to get the symbols in the addition subtraction equation
        // We remove all spaces and underscores in the question format, which leaves all of the symbols
        problemFormat = problemFormat.Replace(" ", "");
        problemFormat = problemFormat.Replace("_", "");


        int remainder = 0;

        // Based on the specific code, we can solve the answer
        switch (problemFormat)
        {
            // Easy questions
            case $"x={QUESTION_KEY}":
                quotient = (randomNumbers[0] * randomNumbers[1]);
                break;
            case $"/={QUESTION_KEY}":
                problem = $"{randomNumbers[0] * randomNumbers[1]} / {randomNumbers[1]} = {QUESTION_KEY}";
                quotient = (randomNumbers[0]);
                break;
            case $"{QUESTION_KEY}x=":
                problem = $"{QUESTION_KEY} x {randomNumbers[1]} = {randomNumbers[0] * randomNumbers[1]}";
                quotient = (randomNumbers[0]);
                break;
            case $"{QUESTION_KEY}/=":
                problem = $"{QUESTION_KEY} / {randomNumbers[0]} = {randomNumbers[1]}";
                quotient = (randomNumbers[0] * randomNumbers[1]);
                break;

            // Special Cases (REMAINDERS)
            case $"r/={QUESTION_KEY}":

                // Recalculating random numbers to make the first number larger than the second number
                int half = ((max - min) / 2);
                randomNumbers[0] = rand.Next(max - half, max);
                randomNumbers[1] = rand.Next(min, min + half);

                quotient = randomNumbers[0] / randomNumbers[1];
                remainder = randomNumbers[0] % randomNumbers[1];

                problem = $"{randomNumbers[0]} / {randomNumbers[1]} = {QUESTION_KEY}";

                break; 

            default:
                throw new Exception("SYMBOL CODE NOT FOUND");
        }
        
        // Now generate the wrong answers
        int rangeOfWrongAnswers = 10;

        // If theres a remainder than all of the wrong answers need remainders aswell
        if(remainder != 0)
        {
            (int, int) remainderAnswer = (quotient, remainder);
            int rangeOfRemainderAnswers = 4;

            (int, int)[] existingRemainderOptions = new (int, int)[3];
            existingRemainderOptions[0] = remainderAnswer;

            (int, int) currentRandomAnswer = (0, 0);
            
            currentRandomAnswer = GenerateWrongRemainderAnswers(rangeOfWrongAnswers, rangeOfRemainderAnswers, (quotient, remainder), existingRemainderOptions);
            wrong[0] = $"{currentRandomAnswer.Item1} R{currentRandomAnswer.Item2}";
            existingRemainderOptions[1] = currentRandomAnswer;

            currentRandomAnswer = GenerateWrongRemainderAnswers(rangeOfWrongAnswers, rangeOfRemainderAnswers, (quotient, remainder), existingRemainderOptions);
            wrong[1] = $"{currentRandomAnswer.Item1} R{currentRandomAnswer.Item2}";
            existingRemainderOptions[2] = currentRandomAnswer;

            currentRandomAnswer = GenerateWrongRemainderAnswers(rangeOfWrongAnswers, rangeOfRemainderAnswers, (quotient, remainder), existingRemainderOptions);
            wrong[2] = $"{currentRandomAnswer.Item1} R{currentRandomAnswer.Item2}";

            return new Question(problem, $"{remainderAnswer.Item1} R{remainderAnswer.Item2}", wrong);
        }

        
        int[] existingOptions = new int[3];
        existingOptions[0] = quotient;

        wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, quotient, existingOptions, false).ToString();
        existingOptions[1] = int.Parse(wrong[0]);
        wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, quotient, existingOptions, false).ToString();
        existingOptions[2] = int.Parse(wrong[1]);
        wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, quotient, existingOptions, false).ToString();

        return new Question(problem, quotient.ToString(), wrong);
    }

    private static Question GeometryConverter(QuestionFormat questionFormat) 
    {
        // Get data from the question format
        string problem = questionFormat.ProblemFormat.Substring(1); // ignore the first character since its a symbol
        string problemFormat = questionFormat.ProblemFormat;
        int min = int.Parse(questionFormat.Min);
        int max = int.Parse(questionFormat.Max);
        float answer = 0;
        string[] wrong = new string[3];

        // Some error checks here
        ErrorChecks(problem, min, max);

        // Determining how many underscores need to be replaced and where in the string they are at
        List<int> randomNumbers = new List<int>();

        problem = GetUnderscores(randomNumbers, problem, min, max);

        // Change the random numbers to floats for geometry problems
        List<float> randomNumbersFloat = randomNumbers.ConvertAll(x => (float)x);

        // Now we move on to figuring out the answer
        // Each question has a unique char in the front, which helps identify the question

        bool includesPi = false;
        (int, int) rootAnswer = (0, 0);

        switch (problemFormat[0])
        {
            // Easy
            case 'a':
                answer = (randomNumbersFloat[0] * randomNumbersFloat[1])/2;
                break;
            case 'b':
                includesPi = true;
                answer = (randomNumbersFloat[0] * 2);
                break;
            case 'c':
                answer = (randomNumbersFloat[0] * randomNumbersFloat[1]);
                break;
            // Medium
            case 'd':
                includesPi = true;
                answer = (randomNumbersFloat[0] * randomNumbersFloat[0])/4;
                break;
                // Special case where we deal with roots
            case 'e':
                // root(a^2 + b^2)
                answer = randomNumbers[0] * randomNumbers[0] + randomNumbers[1] * randomNumbers[1];
                rootAnswer = SimplifyRoot((int)answer);
                break;
            case 'f':
                answer = randomNumbersFloat[0] * 4;
                break;
            default:
                throw new Exception("SYMBOL CODE NOT FOUND");
        }

        if (rootAnswer != (0, 0))
        {
            // We have to generate special wrong answers for roots
            int rangeOfWrongInsides = 4;

            (int, int)[] existingRootOptions = new (int, int)[3];
            existingRootOptions[0] = rootAnswer;

            (int, int) currentWrongOption = GenerateWrongRootAnswer(rangeOfWrongInsides, (int)answer, existingRootOptions);
            wrong[0] = FormatRootAnswer(currentWrongOption);
            existingRootOptions[1] = currentWrongOption;
            

            currentWrongOption = GenerateWrongRootAnswer(rangeOfWrongInsides, (int)answer, existingRootOptions);
            wrong[1] = FormatRootAnswer(currentWrongOption);
            existingRootOptions[2] = currentWrongOption;
           

            currentWrongOption = GenerateWrongRootAnswer(rangeOfWrongInsides, (int)answer, existingRootOptions);
            wrong[2] = FormatRootAnswer(currentWrongOption);

            return new Question(problem, FormatRootAnswer(rootAnswer), wrong);
        }

        // Now generate the wrong answers
        int rangeOfWrongAnswers = 10;
        float[] existingOptions = new float[3];
        existingOptions[0] = answer;

        wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false).ToString("0.##");
        existingOptions[1] = float.Parse(wrong[0]);

        wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false).ToString("0.##");
        existingOptions[2] = float.Parse(wrong[1]);

        wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false).ToString("0.##");

        if (includesPi)
        { 
            for(int i = 0; i < wrong.Length; i++)
            {
                if (wrong[i] == "1")
                    wrong[i] = "π";
                else
                    wrong[i] = $"{wrong[i]}π";
            }

            string answerString = "";
            if (answer == 1)
                answerString = "π";
            else
                answerString = $"{answer.ToString("0.##")}π";

            return new Question(problem, answerString, wrong);
        }

        return new Question(problem, answer.ToString("0.##"), wrong);
    }
    private static void ErrorChecks(string problem, int min, int max)
	{
        if (problem.Length <= 0)
        {
            throw new Exception("Empty problem string");
        }

        if (min > max)
        {
            throw new Exception("Minimum value is less than maximum value");
        }
    }

	private static string GetUnderscores(List<int> randomNumbers, string problem, int min, int max) 
	{
        int currentIndex = problem.IndexOf("_");

        while (currentIndex != -1)
        {
            // Generate a random number
            int randomNumber = rand.Next(min, max);
            randomNumbers.Add(randomNumber);

            // While we do this, update the problem string
            problem = problem.Remove(currentIndex, 1);
            problem = problem.Insert(currentIndex, randomNumber.ToString());

            currentIndex = problem.IndexOf("_");
        }

		return problem;
    }

    // Deals with generating wrong answers for questions with roots
    private static (int, int) GenerateWrongRootAnswer(int rangeOfUnsimplifiedInsides, int unsimplifiedAnswer, (int, int)[] existingOptions)
    {
        (int, int) randomTuple = (0, 0);

        do
        {
            // Genearate a random root tuple
            randomTuple = SimplifyRoot(rand.Next(unsimplifiedAnswer - rangeOfUnsimplifiedInsides/2, unsimplifiedAnswer + rangeOfUnsimplifiedInsides/2));
            
            // Make sure its not one of the other options and the tuple is not negative
        } while (existingOptions.Contains<(int, int)>(randomTuple) || randomTuple.Item1 <= 0 || randomTuple.Item2 <= 0);

        return randomTuple;
    }

    // Deals with generating wrong answers for questions that have remainders
    private static (int, int) GenerateWrongRemainderAnswers(int rangeOfWrongQuotients, int rangeOfWrongRemainders, (int, int) answer, (int,int)[] existingOptions)
    {
        (int, int) randomTuple = (0,0);

        do
        {
            // Generate a random tuple
            // The first being the quotient and the second being the remainder

            randomTuple = 
            (
                rand.Next(answer.Item1 - rangeOfWrongQuotients / 2, answer.Item1 + rangeOfWrongQuotients / 2), 
                rand.Next(answer.Item2 - rangeOfWrongRemainders / 2, answer.Item2 + rangeOfWrongRemainders / 2)
            );

            // Make sure its not one of the other options and the tuple is not negative
        } while (existingOptions.Contains<(int,int)>(randomTuple) || randomTuple.Item1 <= 0 || randomTuple.Item2 <= 0);

        return randomTuple;
    }

    // Deals with generating wrong answers for floats
    private static float GenerateWrongAnswer(int rangeOfWrongAnswers, float answer, float[] existingOptions, bool allowNegative)
    {
        float randomNumber = 0;
        do
        {
            // randomNumber = GD.Randf() * rangeOfWrongAnswers + (answer - rangeOfWrongAnswers / 2);
            randomNumber = answer + (rand.Next(rangeOfWrongAnswers) - rangeOfWrongAnswers / 2);
            // Make sure its not one of the other options and is not negative
        } while (existingOptions.Contains<float>(randomNumber) || (!allowNegative && randomNumber < 0));

        return randomNumber;
    }

    // Deals with generating wrong answers for integers
    private static int GenerateWrongAnswer(int rangeOfWrongAnswers, int answer, int[] existingOptions, bool allowNegative)
	{
		int randomNumber = 0;
		do
		{
			randomNumber = rand.Next(answer - rangeOfWrongAnswers / 2, answer + rangeOfWrongAnswers / 2);
			// Make sure its not one of the other options and is not negative
		} while (existingOptions.Contains<int>(randomNumber) || (!allowNegative && randomNumber < 0));

		return randomNumber;
	}

    private static (int, int) SimplifyRoot(int unsimplifiedInside)
    {
        if(unsimplifiedInside < 0)
        {
            return (0,0);
        }

        int largestSquare = 1;

        // Find the largest perfect square that divides the root
        for(int i = 1; i < unsimplifiedInside; i++)
        {
            if(unsimplifiedInside % (i * i) == 0)
            {
                largestSquare = i * i;
            }
        }

        int outside = (int)Math.Sqrt(largestSquare);
        int inside = unsimplifiedInside / largestSquare;

        return (outside, inside);
    }

    private static string FormatRootAnswer((int, int) rootAnswer)
    {
        if(rootAnswer.Item1 == 1 && rootAnswer.Item2 == 1)
        {
            return "1";
        }

        if (rootAnswer.Item1 == 1)
        {
            return $"√{rootAnswer.Item2}";
        }

        if(rootAnswer.Item2 == 1)
        {
            return $"{rootAnswer.Item1}";
        }

        return $"{rootAnswer.Item1}√{rootAnswer.Item2}";
    }
}
