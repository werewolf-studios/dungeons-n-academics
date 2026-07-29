using Godot;
using System;

public partial class Grid : GridMap
{
    public override void _Ready()
    {
        foreach (Node child in GetChildren())
        {
            if (child is PushBlock box)
            {
                box.Initialize(this);
            }
        }
        
    }
}
