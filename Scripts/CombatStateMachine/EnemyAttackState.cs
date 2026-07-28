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
		GD.Print("EAttkStartTimer started");
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
		GD.Print("EAttkStartTimer timedout");
		player.TakeDamage(enemy.Damage);

		GetNode<Timer>("EAttkEndTimer").Start();
		GD.Print("EAttkEndTimer started");
	}

	private void OnEAttkEndTimerTimeout()
	{
		GD.Print("EAttkEndTimer timedout");
		csm.TransitionTo("PlayerTurnState");
	}
}
