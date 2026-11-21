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

		// Each question starts unanswered; a skipped question must not reuse the last result.
		answerCorrect = false;
		PlayerStatsUI.Visible = true;
		QuestionManager.StartQuestionSequence(Grade.Eighth, QuestionType.Math, Topic.Geometry, currentDifficulty, 1, 20);
    }

	public override void Exit()
	{
		PlayerStatsUI.Visible = false;
	}

	private void OnQuestionsUIQuestionSequenceEnded()
	{
		bool special = Combat != null && Combat.PendingAction == CombatMain.TurnAction.Special;
		// Reset for the next turn before leaving; the next command sets it again.
		if (Combat != null) Combat.PendingAction = CombatMain.TurnAction.Attack;

		if (answerCorrect)
		{
			csm.TransitionTo(special ? "SpecialAttackState" : "PlayerAttackState");
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
