using Godot;

/// <summary>
/// A consumable lying in the level. Walking into it stores one item in the
/// player's inventory, announces the pickup, and removes the pickup.
/// </summary>
public partial class ItemPickup : Area3D
{
    [Export] public string ItemId { get; set; } = ItemCatalog.HealthPotion;

    private Vector3 basePosition;
    private float phase;

    public override void _Ready()
    {
        basePosition = Position;
        phase = (float)GD.RandRange(0.0, Mathf.Tau);
        BodyEntered += OnBodyEntered;
    }

    public override void _Process(double delta)
    {
        // Slow spin plus a shallow bob so pickups read as collectable.
        RotateY((float)delta * 1.4f);
        Position = basePosition + new Vector3(0, Mathf.Sin(phase + (float)Time.GetTicksMsec() / 450f) * 0.08f, 0);
    }

    private void OnBodyEntered(Node3D body)
    {
        if (body is not Player) return;

        var definition = ItemCatalog.Get(ItemId);
        if (definition == null)
        {
            GD.PushError($"ItemPickup: unknown item id '{ItemId}'");
            return;
        }

        SaveManager.Instance.PlayerData.AddItem(ItemId);
        ItemToast.Instance?.ShowMessage($"{definition.DisplayName} was picked up!");
        QueueFree();
    }
}
