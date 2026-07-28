using Godot;
using System;

public partial class QuestionState : CombatState
{
    public override void Enter()
    {
		GD.Print("Entered QuestionState");
        GetNode<Control>("%QuestionUI").Show();
    }

	public override void Exit()
	{
		GetNode<Control>("%QuestionUI").Hide();
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
