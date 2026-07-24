using Godot;
using System;

public partial class Enemy : Node3D
{
    public int strength;
    public int exp;

    public override void _Ready()
    {
        strength = 0; 
        exp = 0;
    }
}
