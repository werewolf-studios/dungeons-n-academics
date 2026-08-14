using Godot;
using System;

public partial class Door : Area3D
{
    // Reference to the Player
    [Export]
    public Player playerRef;

    // Reference to the Camera
    [Export]
    public CameraFollower cameraRef;

    // Where the player starts in the next room
    [Export]
    public Vector3 newPlayerLocation;

    // Where the camera starts in the next room
    [Export]
    public Vector3 newCameraLocation;

    [Export]
    public Vector3 AnswerMoveTo;

    public void ChangeRoom(Node3D body)
    {
        if (body == playerRef)
        {
            playerRef.Position = newPlayerLocation;
            cameraRef.Position = newCameraLocation;
        }
    }

    public void Answered()
    {
        Position = AnswerMoveTo;
    }
}
