using Godot;
using System;

public partial class PlayerAttackState : CombatState
{
	// READ ME!! Timers will need to be reworked and possibly moved elsewhere.
	// As EnemyManager reads, this was a prototype to just get the absolute
	// basics down. Yes the names are quite bad.
	[Export]
	public EnemyManager EnemyManager { get; set; }

    [Export]
    public ProgressBar enemyHealthBar { get; set; }

    [Export]
	public Timer PAttkStartTimer { get; set; }

	[Export]
	public Timer PAttkEndTimer { get; set; }
    public override void Enter()
    {
		GD.Print("Entered PlayerAttackState");
        PAttkStartTimer.Start();
		GD.Print("PAttkStartTimer started");

		PAttkEndTimer.WaitTime = 2.0;
    }

    public override void Exit()
    {
        
    }

	private void OnPAttkStartTimerTimeout()
	{
		GD.Print("PAttkStartTimer timedout");
		EnemyManager.DamageEnemies();
		enemyHealthBar.Value = EnemyManager.getEnemyHealth(0);

		EnemyManager.CheckIfEnemiesDead();

		PAttkEndTimer.Start();
		GD.Print("PAttkEndTimer started");
	}

    private void OnPAttkEndTimerTimeout()
	{
		GD.Print("PAttkEndTimer timedout");

		if (EnemyManager.AllEnemiesDead())
		{
			csm.TransitionTo("VictoryState");
			return;
		}

		csm.TransitionTo("EnemyAttackState");
	}
}
