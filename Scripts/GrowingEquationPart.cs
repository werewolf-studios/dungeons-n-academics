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
        // Send signal to main puzzle system
        if (GetParent() is GrowingEquationManager manager)
        {
            manager.DeviceHit(answers[currentValue].ToString());
        }
    }

    public void IncrementQuestion()
    {
        // Clamp at the last authored option; the manager resets the run instead
        // of letting the index run past the array.
        if (answers == null || currentValue + 1 >= answers.Length)
        {
            return;
        }
        currentValue++;
        GetNode<Label3D>("Text").Text = answers[currentValue].ToString();
    }

    public void Reset()
    {
        // Reset after completion
        currentValue = 0;
        GetNode<Label3D>("Text").Text = answers[currentValue].ToString();
    }
}
