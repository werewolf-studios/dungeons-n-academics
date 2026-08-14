using Godot;
using System;

public partial class TilePickUp : InteractionTest
{
    [Export]
    int index;
    [Export]
    Node3D[] meshes;
    string[] values;

    public override void _Ready()
    {
        meshes[index].Visible = true;
    }

    public string GetValue()
    {
        return values[index];
    }
}
