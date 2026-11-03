using Godot;
using System.Text.Json;

/// <summary>Presentation only. The Player capsule owns all world movement.</summary>
public partial class ExplorationCharacterVisual : Node3D
{
    private const string AssetRoot = "res://Assets/Characters/Animated/v11/";
    [Export] public string CharacterId { get; set; } = "brother";
    public string CurrentClip { get; private set; } = "";
    public AnimationPlayer AnimationPlayer { get; private set; }

    public override void _Ready()
    {
        AnimationPlayer = FindChildOfType<AnimationPlayer>(this);
        var skeleton = FindChildOfType<Skeleton3D>(this);
        using var manifest = JsonDocument.Parse(FileAccess.GetFileAsString(AssetRoot + "animation-manifest.json"));
        var data = manifest.RootElement;

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
        // Combat decides when to show weapons in a later integration.
        var socketData = data.GetProperty("socket");
        var attachment = new BoneAttachment3D { Name = "WeaponAttachment", BoneName = socketData.GetProperty("bone").GetString() };
        skeleton.AddChild(attachment);
        AddWeapon(attachment, "Sword", ReadVector(socketData.GetProperty("position")),
            ReadVector(socketData.GetProperty("sword_rotation_degrees")));
        AddWeapon(attachment, "Spear", ReadVector(socketData.GetProperty("spear_position").GetProperty(CharacterId)),
            ReadVector(socketData.GetProperty("spear_rotation_degrees")));
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

    private static void AddWeapon(Node parent, string weapon, Vector3 position, Vector3 rotation)
    {
        var socket = new Node3D { Name = weapon + "Socket", Position = position, RotationDegrees = rotation, Visible = false };
        parent.AddChild(socket);
        socket.AddChild(GD.Load<PackedScene>("res://Scenes/Weapons/starter_" + weapon.ToLowerInvariant() + ".tscn").Instantiate());
    }

    private static Vector3 ReadVector(JsonElement value) => new(value[0].GetSingle(), value[1].GetSingle(), value[2].GetSingle());

    private static T FindChildOfType<T>(Node node) where T : Node
    {
        if (node is T found) return found;
        foreach (Node child in node.GetChildren())
        {
            var result = FindChildOfType<T>(child);
            if (result != null) return result;
        }
        return null;
    }
}
