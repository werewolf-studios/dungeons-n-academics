using Godot;
using System;

public partial class EnemyAttackState : CombatState
{
	// READ ME!! Timers will need to be reworked and possibly moved elsewhere.
	// As EnemyManager reads, this was a prototype to just get the absolute
	// basics down. Yes the names are quite bad.
	[Export]
	public EnemyManager EnemyManager { get; set; }

	[Export]
	public CombatPlayer player { get; set; }

	[Export]
	public Timer EAttkStartTimer { get; set; }

	[Export]
	public Timer EAttkEndTimer { get; set; }
    public override void Enter()
    {
		GD.Print("Entered EnemyAttackState");
        EAttkStartTimer.Start();
		GD.Print("EAttkStartTimer started");

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

		EAttkEndTimer.Start();
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
