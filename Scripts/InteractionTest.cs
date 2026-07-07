using Godot;
using System;

public partial class InteractionTest : Area3D
{
    // Test with toggle
    [Export]
    private StandardMaterial3D materialA;

    [Export]
    private StandardMaterial3D materialB;

    // Called when the node enters the scene tree for the first time.
    public override void _Ready()
	{
        GetNode<MeshInstance3D>("MeshInstance3D").MaterialOverride = materialA;
    }

	// On Interaction
	public virtual void Interaction(Player origin)
	{
        GD.Print("Interaction Started");

        if (GetNode<MeshInstance3D>("MeshInstance3D").MaterialOverride == materialA)
        {
            GetNode<MeshInstance3D>("MeshInstance3D").MaterialOverride = materialB;
        }
        else
        {
            GetNode<MeshInstance3D>("MeshInstance3D").MaterialOverride = materialA;
        }
	}
}
