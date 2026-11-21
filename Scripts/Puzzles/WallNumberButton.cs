using Godot;

/// <summary>
/// A numbered plaque on the wall. Interacting toggles it in its parent
/// WallButtonPuzzle; selected plaques glow.
/// </summary>
public partial class WallNumberButton : CharacterBody3D
{
    [Export] public int Value { get; set; } = 1;
    [Export] public StandardMaterial3D NormalMaterial { get; set; }
    [Export] public StandardMaterial3D SelectedMaterial { get; set; }

    public bool Selected { get; private set; }

    private WallButtonPuzzle puzzle;
    private MeshInstance3D plaque;
    private Label3D number;

    public override void _Ready()
    {
        plaque = GetNodeOrNull<MeshInstance3D>("MeshInstance3D");
        number = GetNodeOrNull<Label3D>("Number");
        if (number != null)
        {
            number.Text = Value.ToString();
        }
        if (plaque != null)
        {
            plaque.MaterialOverride = NormalMaterial;
        }
    }

    public void SetPuzzle(WallButtonPuzzle owner) => puzzle = owner;

    public void Interaction(Player origin) => puzzle?.Toggle(this);

    public void SetSelected(bool selected)
    {
        Selected = selected;
        if (plaque != null)
        {
            plaque.MaterialOverride = selected ? SelectedMaterial : NormalMaterial;
        }
        if (number != null)
        {
            number.Modulate = selected ? new Color(1f, 1f, 0.55f, 1f) : Colors.White;
        }
    }
}
