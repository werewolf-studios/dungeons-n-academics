using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using static Godot.OpenXRInterface;

public enum QuestionType
{
    Math,
    History
    // Add more question types as needed
}

public enum Topic
{
    AdditionAndSubtraction
    // Add more subjects as needed
}

public enum Difficulty
{
    Easy = 0,
    Medium = 1,
    Hard = 2
}
public partial class QuestionManager : CanvasLayer
{
    // Signal for when the question sequence is over
    [Signal]
    public delegate void QuestionSequenceEndedEventHandler();

    // Signal for when the Question is prompted
    [Signal]
    public delegate void QuestionStartedEventHandler();

    // Signal for when the Answer is Displayed
    [Signal]
    public delegate void AnswerDisplayedEventHandler();

    // Signal for when the player answers the question wrong
    [Signal]
    public delegate void WrongAnswerEventHandler();

    // Signal for when the player answers the question right
    [Signal]
    public delegate void CorrectAnswerEventHandler();

    // Question UI Variables
    [Export]
    private Timer timer;

    [Export]
    private ProgressBar progressBar;

    [Export]
    private Label questionLabel;

    [Export]
    private VBoxContainer buttonContainer;

    [Export]
    private Control blocker;

    private Button choice1;
    private Button choice2;
    private Button choice3;
    private Button choice4;

    private Random random = new Random();

    public override void _Ready()
    {
        SaveManager.Instance.LoadPlayerDataBinary();
        SaveManager.Instance.LoadQuestionDataJson();
        choice1 = buttonContainer.GetChild<Button>(0);
        choice2 = buttonContainer.GetChild<Button>(1);
        choice3 = buttonContainer.GetChild<Button>(2);
        choice4 = buttonContainer.GetChild<Button>(3);
    }

    public override void _Process(double delta)
    {
        // Update progress bar
        progressBar.Value = 100.0 * (timer.TimeLeft / timer.WaitTime);
    }

    private Queue<Question> currentQuestionQueue = new Queue<Question>();

    /// <summary>
    /// Starts a series of multiple choice questions.
    /// </summary>
    /// <param name="questionsType">The type of question</param>
    /// <param name="topic">The topic</param>
    /// <param name="difficulty">The difficulty of the question</param>
    /// <param name="numOfQuestions">The number of questions</param>
    /// <param name="time">The time allocated for each question to be answered</param>
    public void StartQuestionSequence(QuestionType questionsType, Topic topic, Difficulty difficulty, int numOfQuestions, int time)
    {
        
        /*
        List<Question> currentQuestionList = null;

        // Ppulate the current question list with Questions

        if (questionsType == QuestionType.Math)
        {
            currentQuestionList = SaveManager.Instance.MathQuestionsThirdGrade[topic.ToString().ToLower()][(int)difficulty];
        }

        // Check if the questions even exist
        if (currentQuestionList == null)
        {
            GD.PushError("Questions requested do not exist: "+Error.DoesNotExist);
            return;
        }

        // Check if there is enough questions to meet the requested number
        if(currentQuestionList.Count < numOfQuestions)
        {
            GD.PushError("Not enough questions to meet the requested number: " + Error.DoesNotExist);
            return;
        }
        */

        List<QuestionFormat> currentQuestionFormatList = SaveManager.Instance.MathQuestionsThirdGrade[topic.ToString().ToLower()][(int)difficulty];
        if (currentQuestionFormatList == null)
        {
            GD.PushError("Questions requested do not exist: " + Error.DoesNotExist);
            return;
        }

        timer.WaitTime = time;

        // Get some random questions from the list
        for(int i = 0; i < numOfQuestions; i++)
        {
            // Add the question to the queue
            Question randomQuestion = QuestionConversionHandler.AdditionSubtractionConverter(currentQuestionFormatList[random.Next(currentQuestionFormatList.Count)]);
            currentQuestionQueue.Enqueue(randomQuestion);
        }

        DisplayNextQuestion();

        this.Visible = true;
    }
    
    private string correctAnswer;
    private bool didPlayerAnswer;

    /// <summary>
    /// Handles the button press event for the answer choice buttons.
    /// </summary>
    /// <param name="button">The button that was pressed.</param>
    public void OnButtonPressed(Button button)
    {
        if (didPlayerAnswer) return;

        blocker.Visible = true;

        didPlayerAnswer = true;
        timer.Paused = true;
        //timer.Stop();

        if (button.Text == correctAnswer)
        {
            // Award the player if they got the correct answer
            EmitSignal(SignalName.CorrectAnswer);
            SaveManager.Instance.PlayerData.Coins += 10; // Award 10 coins for correct answer
        }
        else
        {
            EmitSignal(SignalName.WrongAnswer);
            // Handle incorrect answer
            SaveManager.Instance.PlayerData.Coins -= 10;
        }
        
        DisplayCorrectAnswer();
    }

    /// <summary>
    /// Handles when the timer runs out.
    /// </summary>
    public void OnTimeout()
    {
        if (didPlayerAnswer) return;
        didPlayerAnswer = true;
        EmitSignal(SignalName.WrongAnswer);
        SaveManager.Instance.PlayerData.Coins -= 10;
        DisplayCorrectAnswer();
    }

    /// <summary>
    /// Displays the correct answer using colors.
    /// </summary>
    /// <returns>Time to display the answer</returns>
    private async Task DisplayCorrectAnswer()
    {
        EmitSignal(SignalName.AnswerDisplayed);
        blocker.Visible = true;
        foreach(Button b in buttonContainer.GetChildren())
        {
            StyleBoxFlat styleBox = b.GetThemeStylebox("normal") as StyleBoxFlat;
            if (b.Text == correctAnswer)
            { 
                styleBox.BgColor = new Color(0, 1, 0); // Green background for correct answer
            }
            else
            {
                styleBox.BgColor = new Color(1, 0, 0); // Red background for incorrect answer
            }
        }        

        await ToSignal(GetTree().CreateTimer(5.0f), "timeout"); // Wait for 5 seconds before moving to the next question

        DisplayNextQuestion();
    }
    
    /// <summary>
    /// Sets up the next question.
    /// </summary>
    private void DisplayNextQuestion()
    {
        // Reset Button colors
        didPlayerAnswer = false;

        StyleBoxFlat styleBox = choice1.GetThemeStylebox("normal") as StyleBoxFlat;
        styleBox.BgColor = new Color(0, 0, 1);

        styleBox = choice2.GetThemeStylebox("normal") as StyleBoxFlat;
        styleBox.BgColor = new Color(0, 0, 1);

        styleBox = choice3.GetThemeStylebox("normal") as StyleBoxFlat;
        styleBox.BgColor = new Color(0, 0, 1);

        styleBox = choice4.GetThemeStylebox("normal") as StyleBoxFlat;
        styleBox.BgColor = new Color(0, 0, 1);

        blocker.Visible = false;

        if (currentQuestionQueue.Count <= 0)
        {
            // All questions have been answered, end the sequence
            this.Visible = false;
            EmitSignal(SignalName.QuestionSequenceEnded);
            return;
        }

        EmitSignal(SignalName.QuestionStarted);
        
        Question question = currentQuestionQueue.Dequeue();
        questionLabel.Text = question.Problem;
        correctAnswer = question.Answer;

        // Populate randomized answer choices
        string[] possibleAnswers =
        {
            correctAnswer,
            question.Wrong[0],
            question.Wrong[1],
            question.Wrong[2]
        };

        // Shuffle the possible answers
        for (int i = possibleAnswers.Length - 1; i > 0; i--)
        {
            int j = random.Next(0, i + 1);

            string temp = possibleAnswers[i];
            possibleAnswers[i] = possibleAnswers[j];
            possibleAnswers[j] = temp;
        }

        // Assign the shuffled answers to the buttons
        choice1.Text = possibleAnswers[0];
        choice2.Text = possibleAnswers[1];
        choice3.Text = possibleAnswers[2];
        choice4.Text = possibleAnswers[3];

        timer.Start();
        timer.Paused = false;
    }
}
