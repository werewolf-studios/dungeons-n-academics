using Godot;
using System;

public partial class PlayerStatsScript : Node
{
	// player stat labels that will be updated
	[Export]
	private Label coinsLabel;

	[Export]
	private Label xpLabel;

	public override void _Ready()
	{
		// Connecting signals to methods so that the UI updates
		SaveManager.Instance.PlayerData.Connect(
			nameof(PlayerSaveData.CoinsChanged),
			new Callable(this, nameof(OnCoinsChanged))
			);

		SaveManager.Instance.PlayerData.Connect(
			nameof(PlayerSaveData.XPChanged),
			new Callable(this, nameof(OnXPChanged))
			);
		// Add more if needed
	}

	// Methods that connect to the signals
	// Add more if needed
	public void OnCoinsChanged(int newCoins)
    {
        coinsLabel.Text = "Coins: " + newCoins;
    }

    public void OnXPChanged(int newXP)
    {
        xpLabel.Text = "XP: " + newXP;
    }
}
