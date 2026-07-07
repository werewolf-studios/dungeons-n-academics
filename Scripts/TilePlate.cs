using Godot;
using System;

public partial class TilePlate : InteractionTest, MathSignal
{
    // Current tile on the plate
    [Export]
    private TilePickUp heldTile;

    public string GetValue() { return heldTile.GetValue(); }

    // Called when the node enters the scene tree for the first time.
    //Makes sure any objects on tile are placed above it
    public override void _Ready()
	{
        if (heldTile != null)
        {
            heldTile.Position = new Vector3(Position.X, Position.Y + 1, Position.Z);
        }
	}

    public override void Interaction(Player origin)
    {
        //Checks to see if player is holding something and if tile is empty
        if (origin.HeldPuzzlePart != null && heldTile == null)
        {
            //Take pickup from player and place it on tile
            heldTile = origin.HeldPuzzlePart;
            origin.HeldPuzzlePart = null;

            heldTile.Reparent(this);
            heldTile.Position = new Vector3(0, 1, 0);
            heldTile.Scale = new Vector3(1, 1, 1);
        }
        //Checks to see if tile is holding something and player isn't holding anything
        else if (origin.HeldPuzzlePart == null && heldTile != null)
        {
            //Gives pickup to player and removes it from tile
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
