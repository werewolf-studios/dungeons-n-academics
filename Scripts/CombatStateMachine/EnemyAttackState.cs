using Godot;
using System;

public partial class EnemyAttackState : CombatState
{
	[Export]
	public EnemyManager EnemyManager { get; set; }

	[Export]
	public CombatPlayer player { get; set; }

    [Export]
    public ProgressBar playerHealthBar { get; set; }

    [Export]
    public ProgressBar enemyHealthBar { get; set; }

    [Export]
	public Timer EAttkStartTimer { get; set; }

	[Export]
	public Timer EAttkEndTimer { get; set; }

    public override void Enter()
    {
        // The enemy may already be dead (killing blow this turn, or a corpse
        // whose node is still animating). Never let a dead enemy act.
        if (!EnemyManager.AnyEnemyAlive())
        {
            csm.TransitionTo("VictoryState");
            return;
        }

		enemyHealthBar.Value = EnemyManager.getEnemyHealth(0);
		GD.Print("Entered EnemyAttackState");
        EAttkStartTimer.Start();
		EnemyManager.PlayAttackAnim();
    }

    public override void Exit()
    {
        
    }

	private void OnEAttkStartTimerTimeout()
	{
		if (!EnemyManager.AnyEnemyAlive())
		{
			csm.TransitionTo("VictoryState");
			return;
		}

		EnemyManager.DealDamage();
		playerHealthBar.Value = player.health;

		// Flinch and return to Idle, or fall and hold the defeat pose.
		if (player.health <= 0)
		{
			player.PlayDefeated();
		}
		else
		{
			player.PlayHurt();
		}

		EAttkEndTimer.Start();
		EnemyManager.PlayIdleAnim();
	}

	private void OnEAttkEndTimerTimeout()
	{
		if (player.health <= 0)
		{
			csm.TransitionTo("DefeatedState");
			return;
		}

		if (!EnemyManager.AnyEnemyAlive())
		{
			csm.TransitionTo("VictoryState");
			return;
		}

		csm.TransitionTo("PlayerTurnState");
	}
}
