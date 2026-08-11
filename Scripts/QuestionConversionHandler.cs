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

		if(topic == Topic.ImaginaryNumbers)
		{
			return ImaginaryNumbersConverter(questionFormat);
		}

		if(topic == Topic.RationalNumbers)
		{
			return RationalNumbersConverter(questionFormat);
		}

		if(topic == Topic.SlopeIntercept)
		{
			return SlopeInterceptConverter(questionFormat);
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
		int answer = 0;
		string[] wrong = new string[3];

		// Some error checks here
		ErrorChecks(problem, min, max);

		// Determining how many underscores need to be replaced and where in the string they are at
		List<int> randomNumbers = new List<int>();

		problem = GetUnderscores(randomNumbers, problem, min, max);

		// Now we move on to figuring out the answer
		// Each question has a unique char in the front, which helps identify the question

		bool includesPi = false;
		(int, int) rootAnswer = (0, 0);
		(int, int) fractionAnswer = (0, 0);

		switch (problemFormat[0])
		{
			// Easy
			case 'a':
				fractionAnswer = SimplifyFraction((randomNumbers[0] * randomNumbers[1], 2));
				break;
			case 'b':
				includesPi = true;
				answer = (randomNumbers[0] * 2);
				break;
			case 'c':
				answer = (randomNumbers[0] * randomNumbers[1]);
				break;
			// Medium
			case 'd':
				includesPi = true;
				fractionAnswer = SimplifyFraction((randomNumbers[0] * randomNumbers[0], 4));    
				break;
				// Special case where we deal with roots
			case 'e':
				// root(a^2 + b^2)
				answer = randomNumbers[0] * randomNumbers[0] + randomNumbers[1] * randomNumbers[1];
				rootAnswer = SimplifyRoot((int)answer);
				break;
			case 'f':
				answer = randomNumbers[0] * 4;
				break;
			// Hard
			case 'g':
				includesPi = true;
				randomNumbers[0] = rand.Next(1, 360);
				problem = $"Find the arc length of a circle sector with central angle {randomNumbers[0]} degrees and radius {randomNumbers[1]}";
				fractionAnswer = SimplifyFraction((randomNumbers[0] * randomNumbers[1] * 2, 360));
				break;
			case 'h':
				// (l+w)*h/2
				fractionAnswer = SimplifyFraction(((randomNumbers[0] + randomNumbers[1]) * randomNumbers[2], 2));
				break;
			case 'i':
				// 2(lw + lh + wh)
				answer = 2 * (randomNumbers[0] * randomNumbers[1] + randomNumbers[0] * randomNumbers[2] + randomNumbers[1] * randomNumbers[2]);
				break;
			default:
				throw new Exception("SYMBOL CODE NOT FOUND");
		}

		// Now generate the wrong answers
		
		// In the case of a fraction answer
		if(fractionAnswer != (0,0))
		{
			// We have to generate special wrong answers for fractions
			int rangeOfWrongNumerators = 4;
			int rangeOfWrongDenominators = 4;
			(int, int)[] existingFractionOptions = new (int, int)[3];
			existingFractionOptions[0] = fractionAnswer;

			(int, int) currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, fractionAnswer, existingFractionOptions);
			wrong[0] = FormatFractionAnswer(currentWrongOption);
			existingFractionOptions[1] = currentWrongOption;

			currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, fractionAnswer, existingFractionOptions);
			wrong[1] = FormatFractionAnswer(currentWrongOption);
			existingFractionOptions[2] = currentWrongOption;

			currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, fractionAnswer, existingFractionOptions);
			wrong[2] = FormatFractionAnswer(currentWrongOption);

			if (includesPi)
			{
				for(int i = 0; i < wrong.Length; i++)
				{
					if (wrong[i] == "1")
						wrong[i] = "π";
					else
						wrong[i] = $"({wrong[i]})π";
				}
				return new Question(problem, $"({FormatFractionAnswer(fractionAnswer)})π", wrong);
			}

			return new Question(problem, FormatFractionAnswer(fractionAnswer), wrong);
		}

		// In the case of a root answer
		if (rootAnswer != (0, 0))
		{
			// We have to generate special wrong answers for roots
			int rangeOfWrongInsides = 4;

			(int, int)[] existingRootOptions = new (int, int)[3];
			existingRootOptions[0] = rootAnswer;

			(int, int) currentWrongOption = GenerateWrongRootAnswer(rangeOfWrongInsides, answer, existingRootOptions);
			wrong[0] = FormatRootAnswer(currentWrongOption);
			existingRootOptions[1] = currentWrongOption;
			

			currentWrongOption = GenerateWrongRootAnswer(rangeOfWrongInsides, answer, existingRootOptions);
			wrong[1] = FormatRootAnswer(currentWrongOption);
			existingRootOptions[2] = currentWrongOption;
		   

			currentWrongOption = GenerateWrongRootAnswer(rangeOfWrongInsides, answer, existingRootOptions);
			wrong[2] = FormatRootAnswer(currentWrongOption);

			return new Question(problem, FormatRootAnswer(rootAnswer), wrong);
		}

		// In this case we are dealing with a normal integer answer

		int rangeOfWrongAnswers = 10;
		int[] existingOptions = new int[3];
		existingOptions[0] = answer;

		int currentWrongInt = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false);
		wrong[0] = currentWrongInt.ToString();
		existingOptions[1] = currentWrongInt;

		currentWrongInt = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false);
		wrong[1] = currentWrongInt.ToString();
		existingOptions[2] = currentWrongInt;

		currentWrongInt = GenerateWrongAnswer(rangeOfWrongAnswers, answer, existingOptions, false);
		wrong[2] = currentWrongInt.ToString();

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

	// ============================================================
	// Imaginary Numbers Prototype 1
	//   'a'  ->  "i^_"                       simplify i^n
	//   'b'  ->  "√(-_)"                     simplify sqrt of a negative number
	//   'c'  ->  "(_+_i)+(_+_i)"             add two complex numbers
	//   'd'  ->  "(_+_i)(_+_i)"              multiply two complex numbers
	// ============================================================
	private static Question ImaginaryNumbersConverter(QuestionFormat questionFormat)
	{
		string problem = questionFormat.ProblemFormat.Substring(1); 
		char type = questionFormat.ProblemFormat[0];
		int min = int.Parse(questionFormat.Min);
		int max = int.Parse(questionFormat.Max);
		string[] wrong = new string[3];
		string answer;

		ErrorChecks(problem, min, max);

		List<int> randomNumbers = new List<int>();
		problem = GetUnderscores(randomNumbers, problem, min, max);

		switch (type)
		{
			// Simplify i^n using the i, -1, -i, 1 cycle
			case 'a':
			{
				int n = randomNumbers[0] % 4;
				if (n < 0) n += 4;

				string[] cycle = { "1", "i", "-1", "-i" };
				answer = cycle[n];

				string[] existingOptions = new string[3];
				existingOptions[0] = answer;

				wrong[0] = GenerateWrongCycleAnswer(cycle, existingOptions);
				existingOptions[1] = wrong[0];
				wrong[1] = GenerateWrongCycleAnswer(cycle, existingOptions);
				existingOptions[2] = wrong[1];
				wrong[2] = GenerateWrongCycleAnswer(cycle, existingOptions);

				return new Question(problem, answer, wrong);
			}
			// Simplify sqrt(-n) into bi or bi root(c) form
			case 'b':
			{
				int n = randomNumbers[0];
				(int, int) simplified = SimplifyRoot(n);
				answer = FormatImaginaryRoot(simplified);

				int rangeOfWrongInsides = 4;
				(int, int)[] existingOptions = new (int, int)[3];
				existingOptions[0] = simplified;

				(int, int) wrongNum = GenerateWrongRootAnswer(rangeOfWrongInsides, n, existingOptions);
				wrong[0] = FormatImaginaryRoot(wrongNum);
				existingOptions[1] = wrongNum;

				wrongNum = GenerateWrongRootAnswer(rangeOfWrongInsides, n, existingOptions);
				wrong[1] = FormatImaginaryRoot(wrongNum);
				existingOptions[2] = wrongNum;

				wrongNum = GenerateWrongRootAnswer(rangeOfWrongInsides, n, existingOptions);
				wrong[2] = FormatImaginaryRoot(wrongNum);

				return new Question(problem, answer, wrong);
			}
			// Add two complex numbers: (a+bi)+(c+di) = (a+c)+(b+d)i
			case 'c':
			{
				int realPart = randomNumbers[0] + randomNumbers[2];
				int imagPart = randomNumbers[1] + randomNumbers[3];
				answer = FormatComplexAnswer(realPart, imagPart);

				int range = 4;
				(int, int)[] existingOptions = new (int, int)[3];
				existingOptions[0] = (realPart, imagPart);

				(int, int) wrongNum = GenerateWrongComplexAnswer(range, (realPart, imagPart), existingOptions);
				wrong[0] = FormatComplexAnswer(wrongNum.Item1, wrongNum.Item2);
				existingOptions[1] = wrongNum;

				wrongNum = GenerateWrongComplexAnswer(range, (realPart, imagPart), existingOptions);
				wrong[1] = FormatComplexAnswer(wrongNum.Item1, wrongNum.Item2);
				existingOptions[2] = wrongNum;

				wrongNum = GenerateWrongComplexAnswer(range, (realPart, imagPart), existingOptions);
				wrong[2] = FormatComplexAnswer(wrongNum.Item1, wrongNum.Item2);

				return new Question(problem, answer, wrong);
			}
			// Multiply two complex numbers: (a+bi)(c+di) = (ac-bd)+(ad+bc)i
			case 'd':
			{
				int a = randomNumbers[0], b = randomNumbers[1], c = randomNumbers[2], d = randomNumbers[3];
				int realPart = a * c - b * d;
				int imagPart = a * d + b * c;
				answer = FormatComplexAnswer(realPart, imagPart);

				int range = 6;
				(int, int)[] existingOptions = new (int, int)[3];
				existingOptions[0] = (realPart, imagPart);

				(int, int) wrongNum = GenerateWrongComplexAnswer(range, (realPart, imagPart), existingOptions);
				wrong[0] = FormatComplexAnswer(wrongNum.Item1, wrongNum.Item2);
				existingOptions[1] = wrongNum;

				wrongNum = GenerateWrongComplexAnswer(range, (realPart, imagPart), existingOptions);
				wrong[1] = FormatComplexAnswer(wrongNum.Item1, wrongNum.Item2);
				existingOptions[2] = wrongNum;

				wrongNum = GenerateWrongComplexAnswer(range, (realPart, imagPart), existingOptions);
				wrong[2] = FormatComplexAnswer(wrongNum.Item1, wrongNum.Item2);

				return new Question(problem, answer, wrong);
			}
			default:
				throw new Exception("SYMBOL CODE NOT FOUND");
		}
	}

	// ============================================================
	// Rational Numbers Prototype 1
	//   'a'  ->  "_/_+_/_"    add fractions
	//   'b'  ->  "_/_-_/_"    subtract fractions (rerolls on negative result)
	//   'c'  ->  "_/_x_/_"    multiply fractions
	//   'd'  ->  "_/_÷_/_"    divide fractions (Min should exclude 0 for the 2nd numerator)
	//   'e'  ->  "_/_"        simplify a fraction to lowest terms
	//   'f'  ->  "_/_"        convert a fraction to a decimal (rounded to 2 places)
	// ============================================================
	private static Question RationalNumbersConverter(QuestionFormat questionFormat)
	{
		// ignore the first character since its a symbol so there's no confusion
		string problem = questionFormat.ProblemFormat.Substring(1); 
		char type = questionFormat.ProblemFormat[0];
		int min = int.Parse(questionFormat.Min);
		int max = int.Parse(questionFormat.Max);
		string[] wrong = new string[3];

		ErrorChecks(problem, min, max);

		List<int> randomNumbers = new List<int>();
		problem = GetUnderscores(randomNumbers, problem, min, max);

		(int, int) fractionAnswer = (0, 0);
		double decimalAnswer = 0;
		bool isDecimal = false;

		switch (type)
		{
			// add: n1/d1 + n2/d2
			case 'a': 
			{
				int n1 = randomNumbers[0], d1 = randomNumbers[1], n2 = randomNumbers[2], d2 = randomNumbers[3];
				fractionAnswer = SimplifyFraction((n1 * d2 + n2 * d1, d1 * d2));
				break;
			}
			// subtract: n1/d1 - n2/d2
			case 'b': 
			{
				int n1 = randomNumbers[0], d1 = randomNumbers[1], n2 = randomNumbers[2], d2 = randomNumbers[3];
				fractionAnswer = SimplifyFraction((n1 * d2 - n2 * d1, d1 * d2));

				if (fractionAnswer.Item1 < 0)
				{
					// Reroll to avoid negative answers, same pattern used in AdditionSubtractionConverter
					return RationalNumbersConverter(questionFormat);
				}
				break;
			}
			// multiply: n1/d1 x n2/d2
			case 'c': 
			{
				int n1 = randomNumbers[0], d1 = randomNumbers[1], n2 = randomNumbers[2], d2 = randomNumbers[3];
				fractionAnswer = SimplifyFraction((n1 * n2, d1 * d2));
				break;
			}
			// divide: (n1/d1) / (n2/d2) = n1/d1 * d2/n2
			case 'd': 
			{
				int n1 = randomNumbers[0], d1 = randomNumbers[1], n2 = randomNumbers[2], d2 = randomNumbers[3];
				fractionAnswer = SimplifyFraction((n1 * d2, d1 * n2));
				break;
			}
			// simplify an already-reducible fraction
			case 'e': 
			{
				int n = randomNumbers[0] * randomNumbers[1];
				int d = randomNumbers[1] * randomNumbers[2];
				fractionAnswer = SimplifyFraction((n, d));
				break;
			}
			// convert a fraction to a decimal
			case 'f': 
			{
				isDecimal = true;
				int n = randomNumbers[0], d = randomNumbers[1];
				decimalAnswer = Math.Round((double)n / d, 2);
				break;
			}
			default:
				throw new Exception("SYMBOL CODE NOT FOUND");
		}

		if (isDecimal)
		{
			string answerStr = decimalAnswer.ToString("0.##");

			double[] existingOptions = new double[3];
			existingOptions[0] = decimalAnswer;

			double wrongVal = GenerateWrongDecimalAnswer(decimalAnswer, existingOptions);
			wrong[0] = wrongVal.ToString("0.##");
			existingOptions[1] = wrongVal;

			wrongVal = GenerateWrongDecimalAnswer(decimalAnswer, existingOptions);
			wrong[1] = wrongVal.ToString("0.##");
			existingOptions[2] = wrongVal;

			wrongVal = GenerateWrongDecimalAnswer(decimalAnswer, existingOptions);
			wrong[2] = wrongVal.ToString("0.##");

			return new Question(problem, answerStr, wrong);
		}
		
		int rangeOfWrongNumerators = 4;
		int rangeOfWrongDenominators = 4;
		(int, int)[] existingFractionOptions = new (int, int)[3];
		existingFractionOptions[0] = fractionAnswer;

		(int, int) currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, fractionAnswer, existingFractionOptions);
		wrong[0] = FormatFractionAnswer(currentWrongOption);
		existingFractionOptions[1] = currentWrongOption;

		currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, fractionAnswer, existingFractionOptions);
		wrong[1] = FormatFractionAnswer(currentWrongOption);
		existingFractionOptions[2] = currentWrongOption;

		currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, fractionAnswer, existingFractionOptions);
		wrong[2] = FormatFractionAnswer(currentWrongOption);

		return new Question(problem, FormatFractionAnswer(fractionAnswer), wrong);
	}

	// ============================================================
	// Slope-Intercept Prototype
	//   'a'  ->  "Find the slope through (_, _) and (_, _)"     x1,y1,x2,y2 -> slope
	//   'b'  ->  "Slope _, point (_, _). Find the y-intercept."  m,x,y -> b
	//   'c'  ->  "y = _x + _, find y when x = _"                m,b,x -> y   (order: m, x, b, matching template above)
	// ============================================================
	private static Question SlopeInterceptConverter(QuestionFormat questionFormat)
	{
		string problem = questionFormat.ProblemFormat.Substring(1);
		char type = questionFormat.ProblemFormat[0];
		int min = int.Parse(questionFormat.Min);
		int max = int.Parse(questionFormat.Max);
		string[] wrong = new string[3];

		ErrorChecks(problem, min, max);

		List<int> randomNumbers = new List<int>();
		problem = GetUnderscores(randomNumbers, problem, min, max);

		switch (type)
		{
			// Find slope given two points (x1, y1) (x2, y2)
			case 'a':
			{
				int x1 = randomNumbers[0], y1 = randomNumbers[1], x2 = randomNumbers[2], y2 = randomNumbers[3];

				if (x2 == x1)
				{
					// Would be an undefined (vertical) slope, reroll
					return SlopeInterceptConverter(questionFormat);
				}

				(int, int) slope = SimplifyFraction((y2 - y1, x2 - x1));

				int rangeOfWrongNumerators = 4;
				int rangeOfWrongDenominators = 4;
				(int, int)[] existingFractionOptions = new (int, int)[3];
				existingFractionOptions[0] = slope;

				(int, int) currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, slope, existingFractionOptions);
				wrong[0] = FormatFractionAnswer(currentWrongOption);
				existingFractionOptions[1] = currentWrongOption;

				currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, slope, existingFractionOptions);
				wrong[1] = FormatFractionAnswer(currentWrongOption);
				existingFractionOptions[2] = currentWrongOption;

				currentWrongOption = GenerateWrongFractionAnswer(rangeOfWrongNumerators, rangeOfWrongDenominators, slope, existingFractionOptions);
				wrong[2] = FormatFractionAnswer(currentWrongOption);

				return new Question(problem, FormatFractionAnswer(slope), wrong);
			}
			// Find the y-intercept given a slope (m) and a point (x, y): b = y - m*x
			case 'b':
			{
				int m = randomNumbers[0], x = randomNumbers[1], y = randomNumbers[2];
				int b = y - m * x;

				int rangeOfWrongAnswers = 10;
				int[] existingOptions = new int[3];
				existingOptions[0] = b;

				wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, b, existingOptions, true).ToString();
				existingOptions[1] = int.Parse(wrong[0]);
				wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, b, existingOptions, true).ToString();
				existingOptions[2] = int.Parse(wrong[1]);
				wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, b, existingOptions, true).ToString();

				return new Question(problem, b.ToString(), wrong);
			}
			// Evaluate y given the equation y = mx + b and a value for x
			case 'c':
			{
				int m = randomNumbers[0], x = randomNumbers[1], b = randomNumbers[2];
				int y = m * x + b;

				int rangeOfWrongAnswers = 10;
				int[] existingOptions = new int[3];
				existingOptions[0] = y;

				wrong[0] = GenerateWrongAnswer(rangeOfWrongAnswers, y, existingOptions, true).ToString();
				existingOptions[1] = int.Parse(wrong[0]);
				wrong[1] = GenerateWrongAnswer(rangeOfWrongAnswers, y, existingOptions, true).ToString();
				existingOptions[2] = int.Parse(wrong[1]);
				wrong[2] = GenerateWrongAnswer(rangeOfWrongAnswers, y, existingOptions, true).ToString();

				return new Question(problem, y.ToString(), wrong);
			}
			default:
				throw new Exception("SYMBOL CODE NOT FOUND");
		}
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
		(int, int) randomNum = (0, 0);

		do
		{
			// Genearate a random root Num
			randomNum = SimplifyRoot(rand.Next(unsimplifiedAnswer - rangeOfUnsimplifiedInsides/2, unsimplifiedAnswer + rangeOfUnsimplifiedInsides/2));
			
			// Make sure its not one of the other options and the Num is not negative
		} while (existingOptions.Contains<(int, int)>(randomNum) || randomNum.Item1 <= 0 || randomNum.Item2 <= 0);

		return randomNum;
	}

	// Deals with generating wrong answers for questions that have remainders
	private static (int, int) GenerateWrongRemainderAnswers(int rangeOfQuotients, int rangeOfRemainders, (int, int) answer, (int,int)[] existingOptions)
	{
		(int, int) randomNum = (0,0);

		do
		{
			// Generate a random num the first being the quotient and the second being the remainder
			randomNum = 
			(
				rand.Next(answer.Item1 - rangeOfQuotients / 2, answer.Item1 + rangeOfQuotients / 2), 
				rand.Next(answer.Item2 - rangeOfRemainders / 2, answer.Item2 + rangeOfRemainders / 2)
			);

			// Make sure its not one of the other options and the Num is not negative
		} while (existingOptions.Contains<(int,int)>(randomNum) || randomNum.Item1 <= 0 || randomNum.Item2 <= 0);

		return randomNum;
	}

	private static (int, int) GenerateWrongFractionAnswer(int rangeOfWrongNumerators, int rangeOfWrongDenominators, (int, int) answer, (int, int)[] existingOptions)
	{
		(int, int) randomNum = (0, 0);

		do
		{
			// Generate a random fraction
			// The first being the numerator and the second being the denominator

			randomNum =
			(
				rand.Next(answer.Item1 - rangeOfWrongNumerators / 2, answer.Item1 + rangeOfWrongNumerators / 2),
				rand.Next(answer.Item2 - rangeOfWrongDenominators / 2, answer.Item2 + rangeOfWrongDenominators / 2)
			);

			// We simplify the fraction to make sure we don't have duplicates cuz fractions can be simplified to the same fraction
			randomNum = SimplifyFraction(randomNum);

			// Make sure its not one of the other options and the fraction is not negative
		} while (existingOptions.Contains<(int, int)>(randomNum) || randomNum.Item1 <= 0 || randomNum.Item2 <= 0);
		return randomNum;
	}

	// Deals with generating wrong answers
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

	// Deals with generating wrong answers that must land on a fixed cycle of values (e.g. the four possible simplifications of i^n)
	private static string GenerateWrongCycleAnswer(string[] cycle, string[] existingOptions)
	{
		string candidate;
		do
		{
			candidate = cycle[rand.Next(0, cycle.Length)];
		} while (existingOptions.Contains(candidate));

		return candidate;
	}

	// Deals with generating wrong answers for complex numbers
	private static (int, int) GenerateWrongComplexAnswer(int range, (int, int) answer, (int, int)[] existingOptions)
	{
		(int, int) randomNum;

		do
		{
			randomNum =
			(
				rand.Next(answer.Item1 - range / 2, answer.Item1 + range / 2 + 1),
				rand.Next(answer.Item2 - range / 2, answer.Item2 + range / 2 + 1)
			);

			// Make sure its not one of the other options
		} while (existingOptions.Contains<(int, int)>(randomNum));

		return randomNum;
	}

	//Deals with generating wrong answers for decimal questions
	private static double GenerateWrongDecimalAnswer(double answer, double[] existingOptions)
	{
		double candidate;

		do
		{
			candidate = Math.Round(answer + (rand.NextDouble() * 2 - 1), 2);
			// Make sure is not negative
		} while (existingOptions.Contains(candidate) || candidate < 0);

		return candidate;
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

	private static (int, int) SimplifyFraction((int, int) unsimplifiedFraction)
	{
	  
		int a = unsimplifiedFraction.Item1;
		int b = unsimplifiedFraction.Item2;
		int temp = 0;

		while(b != 0)
		{
			temp = b;
			b = a % b;
			a = temp;
		}

		int gcd = Math.Abs(a);
		
		return (unsimplifiedFraction.Item1 / gcd, unsimplifiedFraction.Item2 / gcd);
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

	private static string FormatFractionAnswer((int, int) fractionAnswer)
	{
		if (fractionAnswer.Item2 == 1)
		{
			return $"{fractionAnswer.Item1}";
		}
		return $"{fractionAnswer.Item1}/{fractionAnswer.Item2}";
	}

	// Formats a simplified root as an imaginary number
	private static string FormatImaginaryRoot((int, int) rootAnswer)
	{
		if (rootAnswer.Item2 == 1)
		{
			return rootAnswer.Item1 == 1 ? "i" : $"{rootAnswer.Item1}i";
		}

		return rootAnswer.Item1 == 1 ? $"i√{rootAnswer.Item2}" : $"{rootAnswer.Item1}i√{rootAnswer.Item2}";
	}
	// tells you if the i is real or not (prints as a number)
	private static string FormatComplexAnswer(int real, int imaginary)
	{
		if (imaginary == 0)
		{
			return $"{real}";
		}

		if (real == 0)
		{
			if (imaginary == 1) return "i";
			if (imaginary == -1) return "-i";
			return $"{imaginary}i";
		}

		string sign = imaginary < 0 ? "-" : "+";
		string imagPart = Math.Abs(imaginary) == 1 ? "i" : $"{Math.Abs(imaginary)}i";

		return $"{real} {sign} {imagPart}";
	}
}
