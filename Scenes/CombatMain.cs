using Godot;
using System;

public partial class CombatMain : Node
{
    private CombatEnemy enemy;
    private CombatPlayer player;
    // Called when the node enters the scene tree for the first time.
    public override void _Ready()
	{
        enemy = GetNode<CombatEnemy>("%CombatEnemy");
        player = GetNodeOrNull<CombatPlayer>("%CombatPlayer");

		enemy.PlayAnim("Idle_Float");
    }

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}

	private void OnAttackButtonPressed()
	{
		
	}

	private void OnAttack1Pressed()
	{
		
	}

	private void OnYesButtonPressed()
	{
		
	}

	private void OnNoButtonPressed()
	{
		
	}
}
