using Godot;
using System;

public partial class Player : Node3D
{
    public int health;
    public int intelligence;
    public int strength;
    public int defense;
    public int exp;

    public override void _Ready()
    {
        health = 100;
        intelligence = 10;
        strength = 10;
        defense = 10;
        exp = 0;
    }
}
