using Godot;
using System;
using System.Runtime.CompilerServices;

/// <summary>
/// Example Script which shows how to use the question system
/// </summary>
public partial class ExampleButtonScript : Button
{
	// You need to have a reference of the question manager in the scene
	[Export]
	private QuestionManager questionManager;

	private Difficulty currentDifficulty = Difficulty.Easy;
	public void OnPressed()
	{
		this.Visible = false;

		// This is how to start a question sequence
        questionManager.StartQuestionSequence(QuestionType.Math, Topic.Geometry, currentDifficulty, 3, 5);
    }

	// You can also use the sequence ended Signal from the QuestionsUI node
	//  if you want something to occur when the sequence has ended
	public void OnQuestionSequenceEnded()
	{
		if (currentDifficulty == Difficulty.Hard) return;

		currentDifficulty++;
		this.Visible = true;
	}
}
