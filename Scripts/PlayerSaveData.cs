using Godot;
using System;

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
    // Add more if needed

    public PlayerSaveDataModel Model { get; private set; } = new PlayerSaveDataModel();

    public void SetModel(PlayerSaveDataModel model)
    {
        Coins = model.Coins;
        XP = model.XP;
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

    // Debounce so that things saving dont overlap and cause errors
    private bool saveQueued = false;
    private void SaveData()
    {
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
        return "Coins: " + Coins + ", XP: " + XP;
    }
}
