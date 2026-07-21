using Godot;
using System;

public partial class TilePickUp : InteractionTest
{
    [Export]
    string value;

    public string GetValue()
    {
        return value;
    }
}
