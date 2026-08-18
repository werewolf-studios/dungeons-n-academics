using Godot;
using System;

public partial class PushButton : InteractionTest, MathSignal
{
	private String setValue;

	public override void _Ready()
	{
		// This scene uses ButtonTop / ButtonBase, not a MeshInstance3D child.
		CallDeferred(MethodName.CheckExistingOverlaps);
	}

	public string GetValue() { GD.Print("Sending");  return setValue; }

	/// <summary>
	/// Stores the block's symbol and asks the parent math puzzle to re-evaluate.
	/// Called by a landing PushBlock and by this button's Area3D overlap.
	/// </summary>
	public void OnBodyEntered(string pushBlockValue)
	{
		GD.Print("Pressed: " + pushBlockValue);
		setValue = pushBlockValue;
		if (GetParent() is MathSystem) { GetParent<MathSystem>().ChangeDetected(); }
	}

	/// <summary>
	/// Area3D body_entered handler. The script stays on the CharacterBody3D root;
	/// the child Area3D is only the overlap sensor.
	/// </summary>
	public void BodyEntered(Node3D body)
	{
		if (body is PushBlock block)
		{
			OnBodyEntered(block.GetValue());
		}
	}

	private void CheckExistingOverlaps()
	{
		Area3D sensor = GetNodeOrNull<Area3D>("Area3D");
		if (sensor == null)
		{
			return;
		}

		foreach (Node3D body in sensor.GetOverlappingBodies())
		{
			BodyEntered(body);
		}
	}
}
