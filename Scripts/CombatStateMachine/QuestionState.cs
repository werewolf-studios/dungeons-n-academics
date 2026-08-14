using Godot;
using System;

public partial class QuestionState : CombatState
{
	[Export]
	public PlayerStatsScript PlayerStatsUI { get; set; }

	[Export]
	public QuestionManager QuestionManager { get; set; }

	// The enumeration is in the QuestionManager script
	private Difficulty currentDifficulty = Difficulty.Easy;

	private bool answerCorrect = false;

    public override void Enter()
    {
		GD.Print("Entered QuestionState");

		PlayerStatsUI.Visible = true;
		QuestionManager.StartQuestionSequence(Grade.Eighth, QuestionType.Math, Topic.Geometry, currentDifficulty, 1, 20);
    }

	public override void Exit()
	{
		PlayerStatsUI.Visible = false;
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
