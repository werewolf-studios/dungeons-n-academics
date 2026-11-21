using Godot;
using System;

public partial class SpecialAttackState : CombatState
{
	// Mirrors PlayerAttackState/timers until the state machine grows a proper
	// command object. The spear thrust is the Special command; it hits harder
	// than the standard sword swing.
	[Export]
	public EnemyManager EnemyManager { get; set; }

	[Export]
	public CombatPlayer player { get; set; }

	[Export]
	public ProgressBar enemyHealthBar { get; set; }

	[Export]
	public Timer PAttkEndTimer { get; set; }

	public const int SpecialDamage = 15;

	public override void Enter()
	{
		GD.Print("Entered SpecialAttackState");
		PAttkEndTimer.WaitTime = 2.0;

		// Damage lands on the spear thrust's contact frame, not on a fixed timer.
		player.SpecialHit += OnPlayerSpecialHit;
		player.PlaySpecial();
	}

	public override void Exit()
	{
		if (player != null)
		{
			player.SpecialHit -= OnPlayerSpecialHit;
		}
	}

	private void OnPlayerSpecialHit()
	{
		GD.Print("Player spear hit");
		player.SpecialHit -= OnPlayerSpecialHit;
		EnemyManager.DamageEnemies(SpecialDamage);
		enemyHealthBar.Value = EnemyManager.getEnemyHealth(0);

		EnemyManager.CheckIfEnemiesDead();

		// A killing hit gets the death animation's full length before victory.
		PAttkEndTimer.WaitTime = EnemyManager.AllEnemiesDead() ? 4.0 : 2.0;
		PAttkEndTimer.Start();
	}

	private void OnPAttkEndTimerTimeout()
	{
		if (EnemyManager.AllEnemiesDead())
		{
			csm.TransitionTo("VictoryState");
			return;
		}

		csm.TransitionTo("EnemyAttackState");
	}
}
