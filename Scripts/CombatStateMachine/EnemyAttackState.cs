using Godot;
using System;

public partial class EnemyAttackState : CombatState
{
	[Export]
	public EnemyManager EnemyManager { get; set; }
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

		// enemy.PlayAnim("Shoot");
		EnemyManager.PlayAttackAnim();
    }

    public override void Exit()
    {
        
    }

	private void OnEAttkStartTimerTimeout()
	{
		GD.Print("EAttkStartTimer timedout");
		// player.TakeDamage(enemy.Damage);
		EnemyManager.DealDamage();

		if (player.health <= 0)
		{
			player.RemoveSelf();
		}

		GetNode<Timer>("EAttkEndTimer").Start();
		GD.Print("EAttkEndTimer started");
		// enemy.PlayAnim("Idle_Float");
		EnemyManager.PlayIdleAnim();
	}

	private void OnEAttkEndTimerTimeout()
	{
		GD.Print("EAttkEndTimer timedout");

		if (player.health <= 0)
		{
			csm.TransitionTo("DefeatedState");
			return;
		}

		csm.TransitionTo("PlayerTurnState");
	}
}
