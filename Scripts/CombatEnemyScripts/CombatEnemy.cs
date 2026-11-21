using Godot;
using System;

public partial class CombatEnemy : Node3D
{
	public int health = 20;
	private int damage = 5;
	private bool dying;

	public bool IsDying => dying;

	public int Damage
	{
		get { return damage; }
		private set { damage = value; }
	}

	public override void _Ready()
	{
		GetNode<CharacterBody3D>("EnemyX").GetNode<AnimationPlayer>("AnimationPlayer").AnimationFinished += OnAnimationFinished;
	}

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

	/// <summary>
	/// Starts the death animation once. The owning attack state decides how long
	/// to wait before victory, so this method no longer reaches into its timer.
	/// </summary>
	public void CheckIfDead()
	{
		if (dying || health > 0)
		{
			return;
		}
		dying = true;
		StopAnim();
		PlayAnim("Death");
	}

	public void RemoveSelf()
	{
		QueueFree();
	}
}
