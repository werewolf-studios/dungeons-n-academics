using Godot;
using System;

public partial class CombatPlayer : Node3D
{
	public int health = 30;
	private int damage = 10;

	public int Damage
	{
		get { return damage; }
		private set { damage = value; }
	}

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}

	public void TakeDamage(int damage)
	{
		health -= damage;
	}

	public void RemoveSelf()
	{
		QueueFree();
	}
}
