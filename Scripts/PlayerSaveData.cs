using Godot;
using System;
using System.Collections.Generic;

/// <summary>
/// An outer facing PlayerSaveDataModel that adds extra functionality that the it cannot have
/// </summary>
public partial class PlayerSaveData : Node
{
    // Signals for when a variable changes
    // Is used with the UI so that it automatically updates when values change
    [Signal]
    public delegate void CoinsChangedEventHandler(int newCoins);

    [Signal]
    public delegate void XPChangedEventHandler(int newXP);

    [Signal]
    public delegate void InventoryChangedEventHandler();

    [Signal]
    public delegate void HealthChangedEventHandler(int newHealth);
    // Add more if needed

    /// <summary>Health ceiling shared by exploration and combat.</summary>
    public const int MaxHealth = 30;

    public PlayerSaveDataModel Model { get; private set; } = new PlayerSaveDataModel();

    public void SetModel(PlayerSaveDataModel model)
    {
        // Load must not auto-save: a save here would write the still-empty
        // inventory over the file before the loaded items are assigned.
        loading = true;
        try
        {
            Model.Items = model.Items != null
                ? new Dictionary<string, int>(model.Items)
                : new Dictionary<string, int>();
            Model.Coins = model.Coins;
            Model.XP = model.XP;
            Model.Health = Math.Clamp(model.Health, 0, MaxHealth);
        }
        finally
        {
            loading = false;
        }

        EmitSignal(SignalName.CoinsChanged, Model.Coins);
        EmitSignal(SignalName.XPChanged, Model.XP);
        EmitSignal(SignalName.InventoryChanged);
        EmitSignal(SignalName.HealthChanged, Model.Health);
        // Add more if needed
    }

    // Player stat properties
    // Add more if needed
    public int Coins 
    { 
        get => Model.Coins; 
        set 
        {
            // update the coins UI text when the coins value is changed
            Model.Coins = value; 
            EmitSignal(SignalName.CoinsChanged, value);
            SaveData();
        }
    }

    public int XP 
    { 
        get => Model.XP; 
        set 
        { 
            // update the XP UI text when the XP value is changed
            Model.XP = value;
            EmitSignal(SignalName.XPChanged, value);
            SaveData();
        } 
    }

    /// <summary>Read-only view of the owned items (id -> count).</summary>
    public IReadOnlyDictionary<string, int> Inventory => Model.Items;

    /// <summary>Current hit points, clamped to 0..MaxHealth and persisted on every change.</summary>
    public int Health
    {
        get => Model.Health;
        set
        {
            int clamped = Math.Clamp(value, 0, MaxHealth);
            Model.Health = clamped;
            EmitSignal(SignalName.HealthChanged, clamped);
            SaveData();
        }
    }

    /// <summary>Restores hit points up to MaxHealth and returns the amount actually healed.</summary>
    public int Heal(int amount)
    {
        int before = Health;
        Health = before + Math.Max(0, amount);
        return Health - before;
    }

    /// <summary>Returns the pool to full (used when a defeat ends a battle).</summary>
    public void ResetHealth() => Health = MaxHealth;

    public int GetItemCount(string itemId) =>
        itemId != null && Model.Items.TryGetValue(itemId, out int count) ? count : 0;

    /// <summary>Adds items and persists the save.</summary>
    public void AddItem(string itemId, int count = 1)
    {
        if (string.IsNullOrEmpty(itemId) || count <= 0) return;
        Model.Items[itemId] = GetItemCount(itemId) + count;
        EmitSignal(SignalName.InventoryChanged);
        SaveData();
    }

    /// <summary>Removes up to <paramref name="count"/> items; false when none were owned.</summary>
    public bool RemoveItem(string itemId, int count = 1)
    {
        if (string.IsNullOrEmpty(itemId) || count <= 0) return false;
        int owned = GetItemCount(itemId);
        if (owned <= 0) return false;

        int remaining = owned - count;
        if (remaining > 0) Model.Items[itemId] = remaining;
        else Model.Items.Remove(itemId);

        EmitSignal(SignalName.InventoryChanged);
        SaveData();
        return true;
    }

    /// <summary>Consumes one of the item; false when none was owned.</summary>
    public bool ConsumeItem(string itemId) => RemoveItem(itemId, 1);

    // Debounce so that things saving dont overlap and cause errors
    private bool saveQueued = false;
    private bool loading = false;
    private void SaveData()
    {
        if (loading) return;
        if (!saveQueued)
        {
            saveQueued = true;
            DoSave();
        }
    }

    private void DoSave()
    {
        SaveManager.Instance.SavePlayerDataBinary();
        SaveManager.Instance.SavePlayerDataJson();
        saveQueued = false;
    }
    public override string ToString()
    {
        return "Coins: " + Coins + ", XP: " + XP + ", Items: " + Model.Items.Count;
    }
}
