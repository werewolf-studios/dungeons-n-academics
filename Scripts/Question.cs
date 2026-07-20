using Godot;
using System;

public class Question
{
	public string Problem { get; set; }
	public string Answer { get; set; }
	public string[] Wrong { get; set; }

    public override string ToString()
    {
        string testString = "Question: " + Problem + "\nCorrect answer: " + Answer + "\nWrong choices: ";
        foreach(string item in Wrong)
        {
            testString += item + " ";
        }
        return testString;
    }
}
