using Godot;
using System.Text.Json;

/// <summary>Shared setup for the approved v10 sibling models, used by exploration and combat.</summary>
public static class CharacterRig
{
    public const string AssetRoot = "res://Assets/Characters/Animated/v10/";

    public static JsonDocument LoadManifest() =>
        JsonDocument.Parse(FileAccess.GetFileAsString(AssetRoot + "animation-manifest.json"));

    /// <summary>
    /// Adds hidden Sword and Spear sockets on the manifest's hand bone.
    /// Callers decide when a weapon is shown.
    /// </summary>
    public static Node3D AttachWeapons(Skeleton3D skeleton, JsonElement manifest, string characterId)
    {
        var socketData = manifest.GetProperty("socket");
        var attachment = new BoneAttachment3D { Name = "WeaponAttachment", BoneName = socketData.GetProperty("bone").GetString() };
        skeleton.AddChild(attachment);
        AddWeapon(attachment, "Sword", ReadVector(socketData.GetProperty("position")),
            ReadVector(socketData.GetProperty("sword_rotation_degrees")));
        AddWeapon(attachment, "Spear", ReadVector(socketData.GetProperty("spear_position").GetProperty(characterId)),
            ReadVector(socketData.GetProperty("spear_rotation_degrees")));
        return attachment;
    }

    public static float EventTime(JsonElement manifest, string clip) =>
        manifest.GetProperty("clips").GetProperty(clip).GetProperty("event_time_seconds").GetSingle();

    public static T FindChildOfType<T>(Node node) where T : Node
    {
        if (node is T found) return found;
        foreach (Node child in node.GetChildren())
        {
            var result = FindChildOfType<T>(child);
            if (result != null) return result;
        }
        return null;
    }

    private static void AddWeapon(Node parent, string weapon, Vector3 position, Vector3 rotation)
    {
        var socket = new Node3D { Name = weapon + "Socket", Position = position, RotationDegrees = rotation, Visible = false };
        parent.AddChild(socket);
        socket.AddChild(GD.Load<PackedScene>("res://Scenes/Weapons/starter_" + weapon.ToLowerInvariant() + ".tscn").Instantiate());
    }

    private static Vector3 ReadVector(JsonElement value) => new(value[0].GetSingle(), value[1].GetSingle(), value[2].GetSingle());
}
