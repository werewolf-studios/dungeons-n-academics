using Godot;
using System;

public partial class VictoryState : CombatState
{
	[Export]
	public Label VictoryText { get; set; }

    public override void Enter()
    {
        VictoryText.Show();
    }
}
