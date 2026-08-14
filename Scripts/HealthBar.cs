using Godot;
using System;

public partial class HealthBar : ProgressBar
{
    [Export]
    public CombatPlayer player { get; set; }

    public virtual void Update()
    {
        Value = player.health;
    }
}
