using Godot;
using System;

public partial class CameraFollower : CharacterBody3D
{
    // Player Reference
    [Export]
    private Player player;

    // How far the player can go without the camera moving
    [Export]
    private float maxCameraDistance;

    // Called when the node enters the scene tree for the first time.
    public override void _Ready()
    {
        Rotation = player.Rotation;
    }

    // Called every frame. 'delta' is the elapsed time since the previous frame.
    public override void _Process(double delta)
    {
        Vector3 previousPosition = Position;
        double distance = Position.DistanceTo(player.Position);
        // GD.Print("Distance: " + distance);

        // Check distance
        if (distance > maxCameraDistance)
        {
            // Move to get back in range
            Velocity = (player.Position - Position).Normalized() * player.Speed;

            MoveAndSlide();

            // Check collision with camera blockers ((Still working on))
            GD.Print(GetSlideCollisionCount());
            if (GetSlideCollisionCount() > 0)
            {
                // Return to previous position in blocked
                Position = previousPosition;
                MoveAndSlide();
            }
        }
    }
}
