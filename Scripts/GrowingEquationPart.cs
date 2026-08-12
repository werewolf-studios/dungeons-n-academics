using Godot;
using System;

public partial class GrowingEquationPart : InteractionTest
{
    private int currentValue = 0;
    [Export]
    private float[] answers;

    public int CurrentValue { get; set; }

    public override void _Ready()
    {
        GetNode<Label3D>("Text").Text = answers[currentValue].ToString();
    }

    public override void Interaction(Player origin)
    {
        if (GetParent() is GrowingEquationManager manager)
        {
            manager.DeviceHit(answers[currentValue].ToString());
        }
    }

    public void IncrementQuestion()
    {
        currentValue++;
        GetNode<Label3D>("Text").Text = answers[currentValue].ToString();
    }

    public void Reset()
    {
        currentValue = 0;
        GetNode<Label3D>("Text").Text = answers[currentValue].ToString();
    }
}
