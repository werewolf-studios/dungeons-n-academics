using Godot;
using System;

public partial class TilePickUp : Area3D
{
    [Export]
    string value;

    public string GetValue()
    {
        return value;
    }
}
