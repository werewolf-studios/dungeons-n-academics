using Godot;
using System;

public partial class CombatEnemy : MeshInstance3D
{
	public int health = 20;
	private int damage = 5;

	public int Damage
	{
		get { return damage; }
		private set { damage = value; }
	}

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		GetNode<CharacterBody3D>("EnemyX").GetNode<AnimationPlayer>("AnimationPlayer").AnimationFinished += OnAnimationFinished;
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}

	public void TakeDamage(int damage)
	{
		health -= damage;
	}

	public void PlayAnim(string animName)
	{
		GetNode<CharacterBody3D>("EnemyX").GetNode<AnimationPlayer>("AnimationPlayer").Play(animName);
    }

	public void StopAnim()
	{
        GetNode<CharacterBody3D>("EnemyX").GetNode<AnimationPlayer>("AnimationPlayer").Stop();
    }

	private void OnAnimationFinished(StringName animName)
	{
		if (animName == "Death")
		{
			RemoveSelf();
		}
    }

	public void CheckIfDead()
	{
		if (health <= 0)
		{
			StopAnim();
			PlayAnim("Death");
			GetNode<Timer>("%PAttkEndTimer").WaitTime = 4.0;
		}
	}

	public void RemoveSelf()
	{
		QueueFree();
	}
}
