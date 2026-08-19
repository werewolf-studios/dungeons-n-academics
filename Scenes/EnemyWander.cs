using Godot;
using System.Collections.Generic;

public partial class EnemyWander : CharacterBody3D
{
	private Node3D pivot;
	private RandomNumberGenerator rng = new RandomNumberGenerator();
	private SceneManager sceneManager;

	private Tween tween;
	private bool isMoving;
	private Vector3 hopStart;
	private Vector3 hopEnd;

	[Export]
	public float moveDistance = 2.5f;

	[Export]
	public float moveDuration = 0.8f;

	[Export]
	public float idleTime = 0.6f;

	[Export]
	public int probeDirections = 8;

	public override void _Ready()
	{
		pivot = GetNodeOrNull<Node3D>("Pivot");
		rng.Randomize();

		Area3D encounterArea = GetNodeOrNull<Area3D>("EncounterArea");
		if (encounterArea != null)
		{
			encounterArea.BodyEntered += OnEncounterAreaBodyEntered;
		}

		Callable.From(StartIdle).CallDeferred();
	}

	public override void _ExitTree()
	{
		StopMotion();
	}

	public void Interaction(Player player)
	{
		TryStartBattle();
	}

	private void OnEncounterAreaBodyEntered(Node3D body)
	{
		if (body is Player)
		{
			TryStartBattle();
		}
	}

	private void TryStartBattle()
	{
		StopMotion();

		if (!GodotObject.IsInstanceValid(sceneManager))
		{
			sceneManager = FindSceneManager();
		}

		sceneManager?.EnterBattle(this);
	}

	private SceneManager FindSceneManager()
	{
		Node node = GetParent();
		while (node != null)
		{
			if (node is SceneManager manager)
			{
				return manager;
			}

			node = node.GetParent();
		}

		return GetTree()?.GetFirstNodeInGroup("SceneManager") as SceneManager;
	}

	private void StartIdle()
	{
		StopMotion();
		if (!IsInsideTree())
		{
			return;
		}

		tween = CreateTween();
		tween.SetProcessMode(Tween.TweenProcessMode.Physics);
		tween.TweenInterval(idleTime);
		tween.Finished += OnIdleFinished;
	}

	private void OnIdleFinished()
	{
		if (!IsInsideTree())
		{
			return;
		}

		TryStartHop();
	}

	private void TryStartHop()
	{
		List<Vector3> open = CollectOpenDirections();
		if (open.Count == 0)
		{
			StartIdle();
			return;
		}

		Vector3 dir = open[rng.RandiRange(0, open.Count - 1)];
		FaceDirection(dir);
		StartHop(dir);
	}

	private List<Vector3> CollectOpenDirections()
	{
		int count = probeDirections <= 4 ? 4 : 8;
		List<Vector3> open = new List<Vector3>(count);

		for (int i = 0; i < count; i++)
		{
			float angle = i * (Mathf.Tau / count);
			Vector3 dir = new Vector3(Mathf.Cos(angle), 0.0f, Mathf.Sin(angle));
			Vector3 motion = dir * moveDistance;
			if (!HitsWall(GlobalTransform, motion))
			{
				open.Add(dir);
			}
		}

		return open;
	}

	private void StartHop(Vector3 dir)
	{
		StopMotion();

		hopStart = GlobalPosition;
		hopEnd = hopStart + dir * moveDistance;
		hopEnd.Y = hopStart.Y;
		isMoving = true;

		tween = CreateTween();
		tween.SetProcessMode(Tween.TweenProcessMode.Physics);
		tween.TweenMethod(new Callable(this, MethodName.ApplyHop), 0.0f, 1.0f, moveDuration)
			.SetEase(Tween.EaseType.Out)
			.SetTrans(Tween.TransitionType.Cubic);
		tween.Finished += OnHopFinished;
	}

	private void ApplyHop(float t)
	{
		if (!isMoving)
		{
			return;
		}

		Vector3 desired = hopStart.Lerp(hopEnd, t);
		desired.Y = hopStart.Y;

		Vector3 motion = desired - GlobalPosition;
		motion.Y = 0.0f;
		if (motion.LengthSquared() < 0.0001f)
		{
			return;
		}

		KinematicCollision3D hit = new KinematicCollision3D();
		if (HitsWall(GlobalTransform, motion, hit))
		{
			AbortHop(hit);
			return;
		}

		GlobalPosition = desired;
	}

	/// <summary>
	/// True when the motion is blocked by a wall or actor. Floor/ceiling hits
	/// (almost-vertical normals) are ignored so a slightly buried collider
	/// does not treat every heading as blocked.
	/// </summary>
	private bool HitsWall(Transform3D from, Vector3 motion, KinematicCollision3D hit = null)
	{
		hit ??= new KinematicCollision3D();
		if (!TestMove(from, motion, hit))
		{
			return false;
		}

		Vector3 wallNormal = hit.GetNormal();
		wallNormal.Y = 0.0f;
		return wallNormal.LengthSquared() > 0.05f;
	}

	private void AbortHop(KinematicCollision3D hit)
	{
		Vector3 travel = hit.GetTravel();
		travel.Y = 0.0f;
		if (travel.LengthSquared() > 0.0001f)
		{
			GlobalPosition += travel;
		}

		StopMotion();

		if (hit.GetCollider() is Player)
		{
			TryStartBattle();
			return;
		}

		StartIdle();
	}

	private void OnHopFinished()
	{
		isMoving = false;
		if (!IsInsideTree())
		{
			return;
		}

		StartIdle();
	}

	private void StopMotion()
	{
		tween?.Kill();
		tween = null;
		isMoving = false;
	}

	private void FaceDirection(Vector3 direction)
	{
		Vector3 lookPos = GlobalPosition + direction;
		lookPos.Y = GlobalPosition.Y;
		if (GlobalPosition.DistanceTo(lookPos) <= 0.01f)
		{
			return;
		}

		// Rotate the visual only. Looking with the CharacterBody3D itself turns the
		// collision box and is what wedges the enemy into walls.
		Node3D face = pivot ?? this;
		face.LookAt(lookPos, Vector3.Up);
		face.RotateObjectLocal(Vector3.Up, Mathf.Pi);
	}
}
