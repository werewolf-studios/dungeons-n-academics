using Godot;
using System;

public partial class PlayerTurnState : CombatState
{
    [Export]
    public Button AttackButton { get; set; }

    [Export]
    public Button ItemsButton { get; set; }

    [Export]
    public Button PlchldrButton { get; set; }

    [Export]
    public Button PlchldrButton2 { get; set; }

    public override void Enter()
    {
        GD.Print("Entered PlayerTurnState");
        AttackButton.Show();
        ItemsButton.Show();
        PlchldrButton.Show();
        PlchldrButton2.Show();
    }

    public override void Exit()
    {
        AttackButton.Hide();
        ItemsButton.Hide();
        PlchldrButton.Hide();
        PlchldrButton2.Hide();
    }

	private void OnAttackButtonPressed()
    {
        csm.TransitionTo("QuestionState");
    }
}