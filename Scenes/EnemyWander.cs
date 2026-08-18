using Godot;
using System;

public partial class EnemyWander : CharacterBody3D
{
    private const int MaxTargetAttempts = 12;
    private const float MinTargetDistance = 2.0f;
    private const float ArrivalDistance = 0.75f;
    private const float StuckMoveThreshold = 0.08f;
    private const float StuckTimeLimit = 0.35f;
    private const float RetargetCooldown = 0.2f;
    private const float Gravity = 20.0f;

    private NavigationAgent3D navAgent;
    private Node3D pivot;
    private RandomNumberGenerator rng = new RandomNumberGenerator();
    private SceneManager sceneManager;

    private Vector3 lastPosition;
    private float stuckTime;
    private float retargetLock;
    private bool hasTarget;

    [Export]
    public int speed = 2;

    [Export]
    public float wanderRadius = 10.0f;

    public override void _Ready()
    {
        navAgent = GetNode<NavigationAgent3D>("NavigationAgent3D");
        navAgent.PathDesiredDistance = 0.5f;
        navAgent.TargetDesiredDistance = ArrivalDistance;

        pivot = GetNodeOrNull<Node3D>("Pivot");
        lastPosition = GlobalPosition;
        rng.Randomize();

        Area3D encounterArea = GetNodeOrNull<Area3D>("EncounterArea");
        if (encounterArea != null)
        {
            encounterArea.BodyEntered += OnEncounterAreaBodyEntered;
        }

        // Wait a physics frame so the navigation map can sync before the first path query.
        Callable.From(PickInitialTarget).CallDeferred();
    }

    private async void PickInitialTarget()
    {
        await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
        MakeNewWanderTarget();
    }

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        retargetLock = Mathf.Max(0.0f, retargetLock - dt);

        if (!hasTarget || navAgent.IsNavigationFinished() || ReachedTarget() || !IsCurrentTargetUsable())
        {
            MakeNewWanderTarget();
        }

        Vector3 nextPoint = hasTarget ? navAgent.GetNextPathPosition() : GlobalPosition;
        Vector3 moveDir = Flatten(nextPoint - GlobalPosition);
        if (moveDir.LengthSquared() < 0.0001f)
        {
            MakeNewWanderTarget();
            moveDir = Flatten(navAgent.TargetPosition - GlobalPosition);
        }

        if (moveDir.LengthSquared() > 0.0001f)
        {
            moveDir = moveDir.Normalized();
            FaceDirection(moveDir);
        }

        Velocity = new Vector3(moveDir.X * speed, Velocity.Y, moveDir.Z * speed);
        if (!IsOnFloor())
        {
            Velocity += Vector3.Down * Gravity * dt;
        }

        MoveAndSlide();
        HandleCollisions(moveDir);
        UpdateStuckTimer(dt);
    }

    /// <summary>
    /// Picks a random wander point. When <paramref name="preferredDirection"/> is set
    /// (usually a wall normal), new points are biased away from the obstacle.
    /// </summary>
    public void MakeNewWanderTarget(Vector3 preferredDirection = default)
    {
        if (retargetLock > 0.0f && hasTarget)
        {
            return;
        }

        Vector3 bias = Flatten(preferredDirection);
        Vector3 chosen = GlobalPosition;
        bool found = false;

        for (int i = 0; i < MaxTargetAttempts; i++)
        {
            float angle = rng.Randf() * Mathf.Tau;
            if (bias.LengthSquared() > 0.0001f)
            {
                float away = Mathf.Atan2(bias.Z, bias.X);
                angle = away + rng.RandfRange(-Mathf.Pi * 0.45f, Mathf.Pi * 0.45f);
            }

            float distance = rng.RandfRange(MinTargetDistance, wanderRadius);
            Vector3 candidate = GlobalPosition + new Vector3(Mathf.Cos(angle), 0.0f, Mathf.Sin(angle)) * distance;
            candidate = ProjectOntoNavigation(candidate);

            if (Flatten(candidate - GlobalPosition).Length() < MinTargetDistance)
            {
                continue;
            }

            chosen = candidate;
            found = true;
            break;
        }

        if (!found)
        {
            Vector3 escape = bias.LengthSquared() > 0.0001f ? bias.Normalized() : Flatten(-Transform.Basis.Z);
            if (escape.LengthSquared() < 0.0001f)
            {
                escape = Vector3.Forward;
            }
            chosen = ProjectOntoNavigation(GlobalPosition + escape * MinTargetDistance);
        }

        navAgent.TargetPosition = chosen;
        hasTarget = true;
        stuckTime = 0.0f;
        retargetLock = RetargetCooldown;
        lastPosition = GlobalPosition;
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

    private void HandleCollisions(Vector3 moveDir)
    {
        Vector3 pushAway = Vector3.Zero;

        for (int i = 0; i < GetSlideCollisionCount(); i++)
        {
            KinematicCollision3D hit = GetSlideCollision(i);
            if (hit.GetCollider() is Player)
            {
                TryStartBattle();
                return;
            }

            Vector3 normal = Flatten(hit.GetNormal());
            if (normal.LengthSquared() < 0.0001f)
            {
                continue;
            }

            // Only retarget when the wall is actually blocking the current heading.
            if (moveDir.LengthSquared() > 0.0001f && normal.Dot(moveDir) > -0.2f)
            {
                continue;
            }

            pushAway += normal;
        }

        if (pushAway.LengthSquared() > 0.0001f)
        {
            MakeNewWanderTarget(pushAway.Normalized());
        }
    }

    private void UpdateStuckTimer(float delta)
    {
        Vector3 moved = Flatten(GlobalPosition - lastPosition);
        lastPosition = GlobalPosition;

        if (moved.Length() < StuckMoveThreshold)
        {
            stuckTime += delta;
        }
        else
        {
            stuckTime = 0.0f;
        }

        if (stuckTime >= StuckTimeLimit)
        {
            stuckTime = 0.0f;
            MakeNewWanderTarget(-Flatten(Velocity));
        }
    }

    private bool ReachedTarget()
    {
        return Flatten(navAgent.TargetPosition - GlobalPosition).Length() <= ArrivalDistance;
    }

    private bool IsCurrentTargetUsable()
    {
        if (navAgent.IsTargetReachable())
        {
            return true;
        }

        // No baked navmesh (the main dungeon sandbox) still walks in a straight line.
        // Treat that as usable and let collision / stuck checks retarget.
        return NavigationServer3D.MapGetIterationId(navAgent.GetNavigationMap()) == 0;
    }

    private Vector3 ProjectOntoNavigation(Vector3 point)
    {
        Rid map = navAgent.GetNavigationMap();
        if (!map.IsValid || NavigationServer3D.MapGetIterationId(map) == 0)
        {
            return point;
        }

        Vector3 closest = NavigationServer3D.MapGetClosestPoint(map, point);
        if (Flatten(closest - point).Length() > wanderRadius)
        {
            return point;
        }

        return new Vector3(closest.X, GlobalPosition.Y, closest.Z);
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

    private static Vector3 Flatten(Vector3 value)
    {
        value.Y = 0.0f;
        return value;
    }
}
