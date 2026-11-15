using Godot;
using System;

public interface MathSignal
{
	// Allows connection of puzzleparts to math systems.
	// Returns null or "" while the part has no value yet (empty plate, unpressed button).
	public string GetValue();
}
