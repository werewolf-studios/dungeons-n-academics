using Godot;
using System;

public class Question
{
	public int Id { get; set; }
	public string Inquiry { get; set; }
	public string Correct { get; set; }
	public string[] Wrong { get; set; }

    public override string ToString()
    {
        string testString = "Question Number: " + Id + "\nQuestion: " + Inquiry + "\nCorrect answer: " + Correct + "\nWrong choices: ";
        foreach(string item in Wrong)
        {
            testString += item + " ";
        }
        return testString;
    }
}
