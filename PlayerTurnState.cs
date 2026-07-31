using Godot;
using System;

public partial class PlayerTurnState : CombatState
{
    public override void Enter()
    {
        GD.Print("Entered PlayerTurnState");
        GetNode<Button>("%AttackButton").Show();
        GetNode<Button>("%ItemsButton").Show();
        GetNode<Button>("%PlchldrButton").Show();
        GetNode<Button>("%PlchldrButton2").Show();
    }

    public override void Exit()
    {
        GetNode<Button>("%AttackButton").Hide();
        GetNode<Button>("%ItemsButton").Hide();
        GetNode<Button>("%PlchldrButton").Hide();
        GetNode<Button>("%PlchldrButton2").Hide();
    }

	private void OnAttackButtonPressed()
    {
        GetNode<Button>("%Attack1").Show();
        GetNode<Button>("%Attack2").Show();
        GetNode<Button>("%Attack3").Show();
        GetNode<Button>("%Attack4").Show();
    }

    private void OnAttack1Pressed()
    {
        GetNode<Button>("%Attack1").Hide();
        GetNode<Button>("%Attack2").Hide();
        GetNode<Button>("%Attack3").Hide();
        GetNode<Button>("%Attack4").Hide();

        csm.TransitionTo("QuestionState");
    }
}