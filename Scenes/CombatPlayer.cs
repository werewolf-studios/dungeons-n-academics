using Godot;
using System;

public partial class CombatPlayer : MeshInstance3D
{
	private int health = 30;
	private int damage = 10;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
