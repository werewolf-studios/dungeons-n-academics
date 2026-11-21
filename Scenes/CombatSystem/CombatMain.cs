using Godot;
using System;

public partial class CombatMain : Node
{
	/// <summary>The player command the pending quiz is gating.</summary>
	public enum TurnAction { Attack, Special }

	[Signal]
	public delegate void BattleFinishedEventHandler(bool playerWon);

	private CombatEnemy enemy;
	private CombatPlayer player;
	private Camera3D combatCamera;
	private bool ending;

	/// <summary>Set by PlayerTurnState before the quiz; read when it resolves.</summary>
	public TurnAction PendingAction { get; set; } = TurnAction.Attack;

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
		// Defeat keeps the zero health; the Game Over screen decides whether to
		// retry (and heal) or return to the title.
		// processAlways: false so the exit delay stops while the game is paused.
		GetTree().CreateTimer(2.0, false).Timeout += () =>
		{
			if (GodotObject.IsInstanceValid(this))
			{
				EmitSignal(SignalName.BattleFinished, playerWon);
			}
		};
	}
}
