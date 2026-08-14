using Godot;
using System;
using System.Collections.Generic;

public partial class MathSystem : Node
{
    [Export]
    float[] answers;

    [Export]
    CharacterBody3D[] puzzleParts;
    Door[] recievers;

    private Expression _expression = new Expression();

    public void ChangeDetected()
	{
        string equation = "";
        Variant result;

        GD.Print("Calculating");

        foreach (var symbol in puzzleParts)
        {
            GD.Print("Checking");
            if (symbol is MathSignal transmitter)
            {
                equation += transmitter.GetValue();
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

                foreach (var number in answers)
                {
                    if (resultNum == number)
                    {
                        GD.Print("Thats Right!");

                        // Send message to object
                    }
                }
            }
        }
    }
}
