using Godot;
using System;

public partial class TilePlate : InteractionTest
{
    // Current tile on the plate
    [Export]
    private TilePickUp heldTile;

    // Called when the node enters the scene tree for the first time.
    public override void _Ready()
	{
        if (heldTile != null)
        {
            heldTile.Position = new Vector3(Position.X, Position.Y + 1, Position.Z);
        }
	}

    public override void Interaction(Player origin)
    {
        if (origin.HeldPuzzlePart != null && heldTile == null)
        {
            heldTile = origin.HeldPuzzlePart;
            origin.HeldPuzzlePart = null;

            heldTile.Reparent(this);
            heldTile.Position = new Vector3(0, 1, 0);
            heldTile.Scale = new Vector3(1, 1, 1);
        }
        else if (origin.HeldPuzzlePart == null && heldTile != null)
        {
            origin.HeldPuzzlePart = heldTile;
            heldTile = null;

            origin.HeldPuzzlePart.Reparent(origin);
            origin.HeldPuzzlePart.Position = new Vector3(0, 2, 0);
            origin.HeldPuzzlePart.Scale = new Vector3(0.5f, 0.5f, 0.5f);
            GD.Print(origin.HeldPuzzlePart.GetParent());
            GD.Print(origin.HeldPuzzlePart.Position);
        }
    }
}
