using Godot;
using System;
using System.Collections.Generic;

/// <summary>
/// The model for the player save data
/// This model is the actual data that is saved
/// </summary>
public class PlayerSaveDataModel
{
	public int Coins { get; set; }
	public int XP { get; set; }

	/// <summary>Current hit points, shared by exploration and combat.</summary>
	public int Health { get; set; } = 30;

	/// <summary>Item id -> owned count. Unknown ids are kept so removing an item definition never deletes progress.</summary>
	public Dictionary<string, int> Items { get; set; } = new();

	// Add more if needed
	// NOTE: if fields are added here, they must be implemented to the playersavedata aswell
}
