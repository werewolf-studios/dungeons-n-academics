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

	public void SetCharacterMale(bool isMale)
	{
		Node3D male = GetNodeOrNull<Node3D>("Male-Character");
		Node3D female = GetNodeOrNull<Node3D>("Female-Character");
		if (male != null)
		{
			male.Visible = isMale;
		}
		if (female != null)
		{
			female.Visible = !isMale;
		}
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
