using Godot;
using System;

public partial class PlayerAttackState : CombatState
{
	private CombatEnemy enemy; 
	private	CombatPlayer player;
    public override void Enter()
    {
		GD.Print("Entered PlayerAttackState");
        GetNode<Timer>("PAttkStartTimer").Start();
		enemy = GetNode<CombatEnemy>("%CombatEnemy");
		player = GetNodeOrNull<CombatPlayer>("%CombatPlayer");

		if (player == null)
		{
			csm.TransitionTo("PlayerTurnState");
			GetNode<Timer>("PAttkStartTimer").Stop();
		}
    }

    public override void Exit()
    {
        
    }

	private void OnPAttkStartTimerTimeout()
	{
		enemy.TakeDamage(player.Damage);

		if (enemy.health <= 0)
		{
			MeshInstance3D currentEnemy = GetNode<MeshInstance3D>("CombatEnemy");
			currentEnemy.QueueFree();
		}

		GetNode<Timer>("PAttkEndTimer").Start();
	}

	private void OnPAttkEndTimerTimeout()
	{
		csm.TransitionTo("EnemyAttackState");
	}
}
