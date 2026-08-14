using Godot;
using System;

public partial class QuestionState : CombatState
{
	//[Export]
	//public NodePath PlayerStatsUI { get; set; }

	//[Export]
	//public NodePath QuestionManager { get; set; }

	private CanvasLayer playerStatsUI;
	private QuestionManager questionManager;

	// The enumeration is in the QuestionManager script
	private Difficulty currentDifficulty = Difficulty.Easy;

	private bool answerCorrect = false;

    public override void _Ready()
    {
        playerStatsUI = GetTree().Root.FindChild("PlayerStatsUI", true, false) as CanvasLayer;
		questionManager = GetTree().Root.FindChild("QuestionsUI", true, false) as QuestionManager;

		if (playerStatsUI == null) GD.Print("PlayerStatsUI completely missing");
		if (questionManager == null) GD.Print("QuestionManager completely missing");
    }

    public override void Enter()
    {
		GD.Print("Entered QuestionState");

		if (playerStatsUI == null || questionManager == null)
		{
			GD.Print("Question system nodes are null");
		}

		playerStatsUI.Visible = true;
		questionManager.StartQuestionSequence(Grade.Eighth, QuestionType.Math, Topic.Geometry, currentDifficulty, 1, 20);
    }

	public override void Exit()
	{
		playerStatsUI.Visible = false;
	}

	private void OnQuestionsUIQuestionSequenceEnded()
	{
		if (answerCorrect)
		{
			csm.TransitionTo("PlayerAttackState");
		}
		else
		{
			csm.TransitionTo("EnemyAttackState");
		}
	}

	private void OnQuestionsUICorrectAnswer()
	{
		answerCorrect = true;
	}

	private void OnQuestionsUIWrongAnswer()
	{
		answerCorrect = false;
	}
}
