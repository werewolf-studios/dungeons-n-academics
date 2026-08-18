using Godot;
using System;

public partial class CombatMain : Node
{
	[Signal]
	public delegate void BattleFinishedEventHandler(bool playerWon);

	private CombatEnemy enemy;
	private CombatPlayer player;
	private Camera3D combatCamera;
	private bool ending;

	public override void _Ready()
	{
		enemy = GetNode<CombatEnemy>("%CombatEnemy");
		player = GetNodeOrNull<CombatPlayer>("%CombatPlayer");
		combatCamera = GetNode<Camera3D>("Camera3D");

		enemy.PlayAnim("Idle_Float");
		combatCamera.MakeCurrent();
	}

	public void ApplyOverworldCharacter(bool isMale)
	{
		player ??= GetNodeOrNull<CombatPlayer>("%CombatPlayer");
		player?.SetCharacterMale(isMale);
	}

	public void NotifyBattleEnded(bool playerWon)
	{
		if (ending)
		{
			return;
		}

		ending = true;
		GetTree().CreateTimer(2.0).Timeout += () =>
		{
			if (GodotObject.IsInstanceValid(this))
			{
				EmitSignal(SignalName.BattleFinished, playerWon);
			}
		};
	}
}
