using Godot;
using System;

public partial class Grid : GridMap
{

    public override void _Ready()
    {
        foreach (Node3D child in GetChildren())
        {
            if (child is PushBlock box)
            {
                box.Initialize(this);
            }
            else
            {
                // *Nonfunctional*
                ////Sets any other objects in gridmap to align with it(such as puzzle walls)
                //Vector3I map = new Vector3I(0, -1, 0);
                //var localPos = this.MapToLocal(Vector3I.Zero);
                //child.GlobalPosition = this.ToGlobal(localPos);
             }
        }
        
    }
}
