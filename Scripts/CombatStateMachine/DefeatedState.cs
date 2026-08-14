using Godot;
using System;

public partial class DefeatedState : CombatState
{
	[Export]
	public Label DefeatedText { get; set; }

    public override void Enter()
    {
        DefeatedText.Show();
    }
}
