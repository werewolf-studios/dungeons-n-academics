using Godot;
using System;
using System.Collections.Generic;

public partial class MathSystem : Node
{
    // Fired once, the first time the equation evaluates to one of the answers.
    [Signal]
    public delegate void SolvedEventHandler();

    [Export]
    float[] answers;

    [Export]
    CharacterBody3D[] puzzleParts;

    // Doors opened when this puzzle is solved.
    [Export]
    Door[] doorsToUnlock = new Door[0];

    public bool IsSolved { get; private set; }

    private Expression _expression = new Expression();

    public void ChangeDetected()
	{
        // Solved puzzles stay solved; moving tiles afterwards doesn't re-lock the door.
        if (IsSolved)
        {
            return;
        }

        string equation = "";
        Variant result;

        GD.Print("Calculating");

        // compile data
        foreach (var symbol in puzzleParts)
        {
            GD.Print("Checking");
            if (symbol is MathSignal transmitter)
            {
                // An empty plate or an unpressed button means the equation isn't finished yet.
                string value = transmitter.GetValue();
                if (string.IsNullOrEmpty(value))
                {
                    GD.Print("Equation incomplete");
                    return;
                }
                equation += value;
                GD.Print(equation);
            }
        }

        // Parse the expression
        Error error = _expression.Parse(equation);

        if (error == Error.Ok)
        {
            // Execute the expression to get the result
            result = _expression.Execute();

            if (!_expression.HasExecuteFailed())
            {
                GD.Print("Result: " + result);
                float resultNum = (float)result;

                // Check if any answers match. Allows multiple answers
                foreach (var number in answers)
                {
                    if (Mathf.IsEqualApprox(resultNum, number))
                    {
                        GD.Print("Thats Right!");
                        OnSolved();
                        return;
                    }
                }
            }
        }
    }

    private void OnSolved()
    {
        IsSolved = true;

        foreach (Door door in doorsToUnlock)
        {
            door?.Unlock();
        }

        EmitSignal(SignalName.Solved);
    }
}
