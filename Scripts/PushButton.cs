using Godot;
using System;

public partial class PushButton : InteractionTest
{
    //Functionality when something touches the button
    public void OnBodyEntered(RigidBody3D pushBlock)
    {
        GD.Print("Pressed");
    }
}
