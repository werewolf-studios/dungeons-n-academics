using Godot;
using System;

public partial class InteractionTest : CharacterBody3D
{
	// Test with toggle
	[Export]
	private StandardMaterial3D materialA;

	[Export]
	private StandardMaterial3D materialB;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		MeshInstance3D mesh = GetNodeOrNull<MeshInstance3D>("MeshInstance3D");
		if (mesh != null)
		{
			mesh.MaterialOverride = materialA;
		}
	}

	// On Interaction
	public virtual void Interaction(Player origin)
	{
		GD.Print("Interaction Started");

		MeshInstance3D mesh = GetNodeOrNull<MeshInstance3D>("MeshInstance3D");
		if (mesh == null)
		{
			return;
		}

		if (mesh.MaterialOverride == materialA)
		{
			mesh.MaterialOverride = materialB;
		}
		else
		{
			mesh.MaterialOverride = materialA;
		}
	}
}
