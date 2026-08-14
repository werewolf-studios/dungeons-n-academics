using Godot;
using System;

public partial class EnemyWander : CharacterBody3D
{
    private NavigationAgent3D navAgent;
    private RandomNumberGenerator rng = new RandomNumberGenerator();

    [Export]
    public int speed = 2;

    [Export]
    public float wanderRadius = 10.0f;

    /// <summary>
    /// Get a reference to the navigation agent
    /// </summary>
    public override void _Ready()
    {
        navAgent = GetNode<NavigationAgent3D>("NavigationAgent3D");
    }

    public override void _PhysicsProcess(double delta)
    {
        //Makes sure agent 
        if (navAgent.IsNavigationFinished())
        {
            MakeNewWanderTarget();
            GD.Print("Done");
            return;
        }

        //calc velocity by getting next path from nav agent's target position
        Vector3 newVel = GlobalPosition.DirectionTo(navAgent.GetNextPathPosition()) * speed;

        //apply velocity, rotation, & moveslide
        Velocity = newVel;
        MoveAndSlide();
    }
    /// <summary>
    /// Calculates a random position vector for the nav agent to wander to 
    /// </summary>
    public void MakeNewWanderTarget()
    {
        double randAngle = rng.Randf() * Math.Tau;
        float randDist = rng.RandfRange(2.0f, wanderRadius);

        float offsetX = (float)Math.Cos(randAngle);
        float offsetZ = (float)Math.Sin(randAngle);

        Vector3 offset = new Vector3(offsetX,0.0f,offsetZ) * randDist;

        Vector3 target = GlobalPosition + offset;

        navAgent.TargetPosition = target;


        // Rotate the enemy towards the target position

        //Lock the X and Z axis, only rotate on Y axis
        Vector3 lookPos = new Vector3(target.X, GlobalPosition.Y, target.Z);

        if (GlobalPosition.DistanceTo(lookPos) > 0.01f) // avoid zero-length errors
        {
            LookAt(lookPos, Vector3.Up);
            //Godot's forward is -Z not +Z(sigh)
            RotateY(Mathf.Pi);
        }

    }
}
