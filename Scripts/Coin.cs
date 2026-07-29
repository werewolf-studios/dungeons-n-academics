using Godot;
using System;

public partial class Coin : Area3D
{
    /// <summary>
    /// Called when the player collides with the object's Area 3D node
    /// </summary>
    /// <param name="player"></param>
    public void OnBodyEntered(CharacterBody3D player)
    {
        //functionality here
        GD.Print("Item Picked Up");

        //deletes object
        QueueFree();
    }
}
