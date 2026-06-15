using Godot;
using System;

public partial class Player : CharacterBody3D
{
    // ///////////////////////////
    // Uses code from 3D tutorial
    // ///////////////////////////

    /* Unsure of use
    // Emitted when the player was hit by an enemy.
    [Signal]
    public delegate void HitEventHandler();
    */

    // How fast the player moves in meters per second.
    [Export]
    public int Speed { get; set; } = 14;

    // The downward acceleration when in the air, in meters per second squared.
    [Export]
    public int FallAcceleration { get; set; } = 75;

    /* Assuming we won't have jumping
    // Vertical impulse applied to the character upon jumping in meters per second.
    [Export]
    public int JumpImpulse { get; set; } = 20;

    // Vertical impulse applied to the character upon bouncing over a mob in meters per second.
    [Export]
    public int BounceImpulse { get; set; } = 16;
    */

    private Vector3 _targetVelocity = Vector3.Zero;

    public override void _PhysicsProcess(double delta)
    {
        // We create a local variable to store the input direction.
        var direction = Vector3.Zero;

        // We check for each move input and update the direction accordingly.
        if (Input.IsActionPressed("(Overworld) Move Right"))
        {
            direction.X -= 1.0f;
        }
        if (Input.IsActionPressed("(Overworld) Move Left"))
        {
            direction.X += 1.0f;
        }
        if (Input.IsActionPressed("(Overworld) Move Up"))
        {
            direction.Z += 1.0f;
        }
        if (Input.IsActionPressed("(Overworld) Move Down"))
        {
            direction.Z -= 1.0f;
        }

        // Prevent diagonal moving fast af
        if (direction != Vector3.Zero)
        {
            direction = direction.Normalized();
            // Setting the basis property will affect the rotation of the node.
            GetNode<Node3D>("Pivot").Basis = Basis.LookingAt(direction);

            // GetNode<AnimationPlayer>("AnimationPlayer").SpeedScale = 4;
        }
        else
        {
            // GetNode<AnimationPlayer>("AnimationPlayer").SpeedScale = 1;
        }

        // Ground Velocity
        _targetVelocity.X = direction.X * Speed;
        _targetVelocity.Z = direction.Z * Speed;

        // Vertical Velocity
        if (!IsOnFloor()) // If in the air, fall towards the floor. Literally gravity
        {
            _targetVelocity.Y -= FallAcceleration * (float)delta;
        }

        /* Assuming we won't have jumping
        // Jumping
        if (IsOnFloor() && Input.IsActionJustPressed("jump"))
        {
            _targetVelocity.Y = JumpImpulse;
        }
        */

        /* Unsure of use
        // Iterate through all collisions that occurred this frame.
        for (int index = 0; index < GetSlideCollisionCount(); index++)
        {
            // We get one of the collisions with the player.
            KinematicCollision3D collision = GetSlideCollision(index);

            // If the collision is with a mob.
            if (collision.GetCollider() is Mob mob)
            {
                // We check that we are hitting it from above.
                if (Vector3.Up.Dot(collision.GetNormal()) > 0.1f)
                {
                    // If so, we squash it and bounce.
                    mob.Squash();
                    _targetVelocity.Y = BounceImpulse;
                    // Prevent further duplicate calls.
                    break;
                }
            }
        }
        */

        // Moving the Character
        Velocity = _targetVelocity;
        MoveAndSlide();

        var pivot = GetNode<Node3D>("Pivot");
        pivot.Rotation = new Vector3(0, pivot.Rotation.Y, pivot.Rotation.Z);
        // pivot.Rotation = new Vector3(Mathf.Pi / 6.0f * Velocity.Y / JumpImpulse, pivot.Rotation.Y, pivot.Rotation.Z);
    }

    // This can be changed later to reflect settings
    // Currently used to test model rendering
    public void SwapCharacter()
    {
        
    }
}
