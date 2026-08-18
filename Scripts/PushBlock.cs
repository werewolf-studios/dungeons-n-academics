using Godot;
using System.Threading.Tasks;

[GlobalClass]
public partial class PushBlock : InteractionTest
{
	int index;
	[Export]
	Node3D[] meshes;
	[Export]
	string[] values;

	GridMap grid;
	bool isMoving = false;
	Tween tween;

	[Export]
	float slidingTime = 0.3f;

	[Export]
	private bool interactRequired;

	public void SetValue(int _index)
	{
		index = _index;
		meshes[index].Visible = true;
	}

	public string GetValue()
	{
		return values[index];
	}

	/// <summary>
	/// Initializes the grid 
	/// </summary>
	/// <param name="_grid"></param>    
	public void Initialize(GridMap _grid)
	{
		grid = _grid;
		//Prevents diagonal movement on first push by ensuring push block is alligned with grid
		GlobalPosition = CalculateDestination(Vector3.Zero);
	}

	public override void Interaction(Player origin)
	{
		_ = Push(GetFacingDirection(origin), true);
	}

	/// <summary>
	/// Checks if the box isn't moving and moves it based on the players collision
	/// </summary>
	/// <param name="velocity"></param>
	/// <returns></returns>
	public async Task Push(Vector3 velocity, bool interactSwitch)
	{
		GD.Print(velocity);
		// Walk-into pushes are ignored when interactRequired is set; interact presses always go through.
		if (grid == null || isMoving || (interactRequired && !interactSwitch))
		{
			return;
		}

		Vector3 moveDir = new Vector3(velocity.X, 0.0f, velocity.Z);
		if (moveDir.LengthSquared() < 0.0001f)
		{
			return;
		}

		Vector3 moveTo = CalculateDestination(moveDir);

		if (CanMove(moveTo))
		{
			//Start tween for smooth box movement 
			tween?.Kill();
			tween = GetTree().CreateTween();
			isMoving = true;
			tween.TweenProperty(this, "global_position", moveTo, slidingTime)
				.SetEase(Tween.EaseType.Out)
				.SetTrans(Tween.TransitionType.Cubic);
			await ToSignal(tween, Tween.SignalName.Finished);
			isMoving = false;

			Area3D sensor = GetNodeOrNull<Area3D>("Area3D");
			if (sensor == null)
			{
				return;
			}

			GD.Print(sensor.GetOverlappingBodies().Count);
			foreach (Node3D hit in sensor.GetOverlappingBodies())
			{
				if (hit is PushButton button)
				{
					button.OnBodyEntered(values[index]);
				}
			}
		}
	}

	/// <summary>
	/// Keeps the push block in the grid by moving it one unit at a time on our GridMap
	/// </summary>
	/// <param name="dir"></param>
	/// <returns></returns>
	public Vector3 CalculateDestination(Vector3 dir)
	{
		// Convert the push into a single cardinal grid step. Lock Y so the block stays on its current cell height.
		Vector3 localDir = grid.GlobalTransform.Basis.Inverse() * dir;
		localDir.Y = 0.0f;

		Vector3I step = Vector3I.Zero;
		if (localDir.LengthSquared() > 0.0001f)
		{
			if (Mathf.Abs(localDir.X) >= Mathf.Abs(localDir.Z))
			{
				step.X = (int)Mathf.Sign(localDir.X);
			}
			else
			{
				step.Z = (int)Mathf.Sign(localDir.Z);
			}
		}

		Vector3 localPos = grid.ToLocal(GlobalPosition);
		Vector3I gridMapPos = grid.LocalToMap(localPos) + step;
		Vector3 localDestination = grid.MapToLocal(gridMapPos);
		return grid.ToGlobal(localDestination);
	}

	/// <summary>
	/// Method used to check if the box is moving or not
	/// </summary>
	/// <param name="moveTo"></param>
	/// <returns></returns>
	public bool CanMove(Vector3 moveTo)
	{
		Transform3D currentTransform = GlobalTransform;
		Vector3 motion = moveTo - GlobalPosition;
		if (motion.LengthSquared() < 0.0001f)
		{
			return false;
		}

		SetCollisionMaskValue(4, false);
		bool hit = TestMove(currentTransform, motion);
		SetCollisionMaskValue(4, true);

		return !hit;
	}

	/// <summary>
	/// Facing comes from the player's pivot. Velocity is zeroed by MoveAndSlide against this block.
	/// </summary>
	private static Vector3 GetFacingDirection(Player origin)
	{
		Node3D pivot = origin.GetNodeOrNull<Node3D>("Pivot");
		if (pivot != null)
		{
			Vector3 facing = -pivot.GlobalTransform.Basis.Z;
			facing.Y = 0.0f;
			if (facing.LengthSquared() > 0.0001f)
			{
				return facing;
			}
		}

		return origin.Velocity;
	}
}
