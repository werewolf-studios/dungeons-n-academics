using Godot;
using System;

/// <summary>
/// The model for the player save data
/// This model is the actual data that is saved
/// </summary>
public class PlayerSaveDataModel
{
	public int Coins { get; set; }
	public int XP { get; set; }

	// Add more if needed
	// NOTE: if fields are added here, they must be implemented to the playersavedata aswell
}
