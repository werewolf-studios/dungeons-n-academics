using Godot;
using System;

public partial class EnemyAttackState : CombatState
{
	private CombatEnemy enemy; 
	private	CombatPlayer player;
    public override void Enter()
    {
		GD.Print("Entered EnemyAttackState");
        GetNode<Timer>("EAttkStartTimer").Start();
		enemy = GetNodeOrNull<CombatEnemy>("%CombatEnemy");
		player = GetNode<CombatPlayer>("%CombatPlayer");

		if (enemy == null)
		{
			csm.TransitionTo("PlayerTurnState");
			GetNode<Timer>("EAttkStartTimer").Stop();
		}
    }

    public override void Exit()
    {
        
    }

	private void OnEAttkStartTimerTimeout()
	{
		player.TakeDamage(enemy.Damage);

		GetNode<Timer>("EAttkEndTimer").Start();
	}

	private void OnEAttkEndTimerTimeout()
	{
		csm.TransitionTo("PlayerTurnState");
	}
}
