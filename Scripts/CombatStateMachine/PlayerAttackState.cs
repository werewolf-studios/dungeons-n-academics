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
		GD.Print("PAttkStartTimer started");

		GetNode<Timer>("PAttkEndTimer").WaitTime = 2.0;

		enemy = GetNode<CombatEnemy>("%CombatEnemy");
		player = GetNodeOrNull<CombatPlayer>("%CombatPlayer");

		if (player == null)
		{
			csm.TransitionTo("PlayerTurnState");
			GetNode<Timer>("PAttkStartTimer").Stop();
		}

		enemy.GetNode<CharacterBody3D>("EnemyX").GetNode<AnimationPlayer>("AnimationPlayer").AnimationFinished += OnAnimationFinished;
    }

    public override void Exit()
    {
        
    }

	private void OnPAttkStartTimerTimeout()
	{
		GD.Print("PAttkStartTimer timedout");
		enemy.TakeDamage(player.Damage);

		if (enemy.health <= 0)
		{
			enemy.StopAnim();
			enemy.PlayAnim("Death");
			GetNode<Timer>("PAttkEndTimer").WaitTime = 4.0;
		}

		GetNode<Timer>("PAttkEndTimer").Start();
		GD.Print("PAttkEndTimer started");
	}

    private void OnAnimationFinished(StringName animName)
	{
		if (animName == "Death")
		{
			MeshInstance3D currentEnemy = GetNode<MeshInstance3D>("%CombatEnemy");
			currentEnemy.QueueFree();
		}
    }

    private void OnPAttkEndTimerTimeout()
	{
		GD.Print("PAttkEndTimer timedout");

		if (enemy.health <= 0)
		{
			csm.TransitionTo("VictoryState");
			return;
		}

		csm.TransitionTo("EnemyAttackState");
	}
}
