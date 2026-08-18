using Godot;
using System;

public partial class SceneManager : Node
{
	[Export]
	public PackedScene CombatScene { get; set; }

	[Export]
	public Camera3D OverworldCamera { get; set; }

	private bool inBattle;
	private Node combatInstance;
	private EnemyWander encounterEnemy;

	public override void _EnterTree()
	{
		AddToGroup("SceneManager");
	}

	public void EnterBattle(EnemyWander enemy)
	{
		if (inBattle || enemy == null)
		{
			return;
		}

		PackedScene scene = CombatScene ?? GD.Load<PackedScene>("res://Scenes/CombatSystem/combat_main.tscn");
		if (scene == null)
		{
			GD.PrintErr("SceneManager: CombatScene is missing.");
			return;
		}

		inBattle = true;
		encounterEnemy = enemy;

		combatInstance = scene.Instantiate();
		AddChild(combatInstance);

		if (combatInstance is CombatMain combatMain)
		{
			combatMain.BattleFinished += ExitBattle;
		}

		SetOverworldIdle(true);
	}

	private void ExitBattle(bool playerWon)
	{
		if (combatInstance is CombatMain combatMain)
		{
			combatMain.BattleFinished -= ExitBattle;
		}

		combatInstance?.QueueFree();
		combatInstance = null;

		if (GodotObject.IsInstanceValid(encounterEnemy))
		{
			encounterEnemy.QueueFree();
		}
		encounterEnemy = null;

		SetOverworldIdle(false);
		Camera3D camera = OverworldCamera ?? GetNodeOrNull<Camera3D>("CameraFollower/CameraPivot/Camera");
		camera?.MakeCurrent();
		inBattle = false;
	}

	private void SetOverworldIdle(bool idle)
	{
		foreach (Node child in GetChildren())
		{
			if (child == combatInstance)
			{
				continue;
			}

			child.ProcessMode = idle ? ProcessModeEnum.Disabled : ProcessModeEnum.Inherit;

			if (child is Node3D node3D)
			{
				node3D.Visible = !idle;
			}
			else if (child is CanvasItem canvasItem)
			{
				canvasItem.Visible = !idle;
			}
		}
	}
}
