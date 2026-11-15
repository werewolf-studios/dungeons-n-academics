using Godot;

/// <summary>
/// A doorway between rooms. Walking into the open doorway's Trigger moves the player
/// (and camera) to the next room. A locked door stays shut until a puzzle calls Unlock().
/// </summary>
public partial class Door : Node3D
{
    [Signal]
    public delegate void OpenedEventHandler();

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

    // Off for a doorway with no room behind it yet: it still opens, but walking in does nothing.
    [Export]
    public bool TeleportEnabled = true;

    // Locked doors stay closed until a puzzle calls Unlock(). Unlocked doors start open.
    [Export]
    public bool StartsLocked = false;

    // Hinge swing in degrees. Negative swings the leaf into the room (local +Z).
    [Export]
    public float OpenAngle = -100.0f;

    [Export]
    public float OpenDuration = 1.6f;

    // Pause between the lock clunk and the leaf starting to swing.
    [Export]
    public float UnlockDelay = 0.35f;

    public bool IsOpen { get; private set; }

    private Node3D hinge;
    private Area3D trigger;
    private AudioStreamPlayer3D unlockAudio;
    private AudioStreamPlayer3D openAudio;
    private Tween tween;

    public override void _Ready()
    {
        hinge = GetNode<Node3D>("Model/DoorHinge");
        trigger = GetNode<Area3D>("Trigger");
        unlockAudio = GetNodeOrNull<AudioStreamPlayer3D>("UnlockAudio");
        openAudio = GetNodeOrNull<AudioStreamPlayer3D>("OpenAudio");

        if (StartsLocked)
        {
            SetClosed();
        }
        else
        {
            SetOpenImmediately();
        }
    }

    public void ChangeRoom(Node3D body)
    {
        if (!IsOpen || !TeleportEnabled || body != playerRef)
        {
            return;
        }

        playerRef.Position = newPlayerLocation;
        if (cameraRef != null)
        {
            cameraRef.Position = newCameraLocation;
        }
    }

    /// <summary>
    /// Opens a locked door with sound and a hinge swing. Safe to call more than once.
    /// </summary>
    public void Unlock()
    {
        if (IsOpen)
        {
            return;
        }
        IsOpen = true;

        unlockAudio?.Play();

        tween?.Kill();
        tween = CreateTween();
        tween.TweenInterval(UnlockDelay);
        tween.TweenCallback(Callable.From(() => openAudio?.Play()));
        tween.TweenProperty(hinge, "rotation_degrees:y", OpenAngle, OpenDuration)
            .SetTrans(Tween.TransitionType.Sine)
            .SetEase(Tween.EaseType.InOut);
        // The doorway only becomes walkable once the leaf has swung clear.
        tween.TweenCallback(Callable.From(() => trigger.SetDeferred(Area3D.PropertyName.Monitoring, true)));
        tween.TweenCallback(Callable.From(() => EmitSignal(SignalName.Opened)));
    }

    // Kept so older callers still work.
    public void Answered()
    {
        Unlock();
    }

    private void SetClosed()
    {
        IsOpen = false;
        hinge.RotationDegrees = new Vector3(0, 0, 0);
        trigger.Monitoring = false;
    }

    private void SetOpenImmediately()
    {
        IsOpen = true;
        hinge.RotationDegrees = new Vector3(0, OpenAngle, 0);
        trigger.Monitoring = true;
    }
}
