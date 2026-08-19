using Godot;
using System;

public partial class TilePickUp : InteractionTest
{
    // Tile Data arrays
    [Export]
    int index;
    [Export]
    Node3D[] meshes;
    [Export]
    string[] values;

    public override void _Ready()
    {
        meshes[index].Visible = true;
    }

    // Send data to plate
    public string GetValue()
    {
        return values[index];
    }
}
