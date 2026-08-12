using Godot;
using System;

public partial class QuestionState : CombatState
{
	[Export]
	public Control QuestionUI { get; set; }
    public override void Enter()
    {
		GD.Print("Entered QuestionState");
        QuestionUI.Show();
    }

	public override void Exit()
	{
		QuestionUI.Hide();
	}

	private void OnYesButtonPressed()
	{
		csm.TransitionTo("PlayerAttackState");
	}

	private void OnNoButtonPressed()
	{
		csm.TransitionTo("EnemyAttackState");
	}
}
