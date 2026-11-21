using System.Collections.Generic;

/// <summary>One consumable's definition. Effects are applied by whoever uses it.</summary>
public sealed class ItemDefinition
{
    public ItemDefinition(string id, string displayName, string description, int heal)
    {
        Id = id;
        DisplayName = displayName;
        Description = description;
        Heal = heal;
    }

    public string Id { get; }
    public string DisplayName { get; }
    public string Description { get; }
    /// <summary>Hit points restored on use; 0 means the item has no battle effect.</summary>
    public int Heal { get; }
}

/// <summary>Static registry of the consumables the prototype ships with.</summary>
public static class ItemCatalog
{
    public const string HealthPotion = "health_potion";
    public const string GreaterElixir = "greater_elixir";

    private static readonly Dictionary<string, ItemDefinition> Items = new()
    {
        [HealthPotion] = new ItemDefinition(HealthPotion, "Health Potion", "Restores 10 HP.", 10),
        [GreaterElixir] = new ItemDefinition(GreaterElixir, "Greater Elixir", "Restores 20 HP.", 20),
    };

    /// <summary>All known items, in a stable display order.</summary>
    public static IEnumerable<ItemDefinition> All => Items.Values;

    public static ItemDefinition Get(string id) =>
        id != null && Items.TryGetValue(id, out var definition) ? definition : null;
}
