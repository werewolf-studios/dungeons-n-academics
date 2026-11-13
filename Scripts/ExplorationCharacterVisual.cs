using Godot;

/// <summary>Presentation only. The Player capsule owns all world movement.</summary>
public partial class ExplorationCharacterVisual : Node3D
{
    [Export] public string CharacterId { get; set; } = "brother";
    public string CurrentClip { get; private set; } = "";
    public AnimationPlayer AnimationPlayer { get; private set; }

    public override void _Ready()
    {
        AnimationPlayer = CharacterRig.FindChildOfType<AnimationPlayer>(this);
        var skeleton = CharacterRig.FindChildOfType<Skeleton3D>(this);
        using var manifest = CharacterRig.LoadManifest();

        // Change loop flags on instance-owned copies, leaving imported v10 resources intact.
        var library = new AnimationLibrary();
        foreach (string clip in new[] { "Idle", "Walk", "Run" })
        {
            var animation = (Animation)AnimationPlayer.GetAnimation(clip).Duplicate();
            animation.LoopMode = Animation.LoopModeEnum.Linear;
            library.AddAnimation(clip, animation);
        }
        AnimationPlayer.AddAnimationLibrary("Exploration", library);

        // Prepare approved sockets; neutral locomotion does not use a weapon grip.
        CharacterRig.AttachWeapons(skeleton, manifest.RootElement, CharacterId);
        UpdateLocomotion(0, false);
    }

    public void UpdateLocomotion(float horizontalSpeed, bool walking)
    {
        string clip = horizontalSpeed < 0.05f ? "Idle" : walking ? "Walk" : "Run";
        // Keep the approved clip timing. Dungeon traversal speed is much higher than
        // the authored stride speed and must not multiply the gait playback rate.
        AnimationPlayer.SpeedScale = 1;
        if (CurrentClip == clip) return;
        CurrentClip = clip;
        AnimationPlayer.Play("Exploration/" + clip, 0.12);
    }
}
