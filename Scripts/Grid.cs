using Godot;
using System;

public partial class Grid : GridMap
{
    public void Ready()
    {
        GD.Print("buh");

        foreach (PushBlock child in GetChildren())
        {
            if (child is PushBlock)
            {
                child.Initialize(this);
            }
        }
        
    }
}
