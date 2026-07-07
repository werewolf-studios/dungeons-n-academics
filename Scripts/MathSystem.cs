using Godot;
using System;
using System.Collections.Generic;

public partial class MathSystem : Node
{
    [Export]
    List<Object> puzzleParts = new List<Object>();

    [Export]
	List<float> answers = new List<float>();

    [Export]
    List<Object> recievers = new List<Object>();

    private Expression _expression = new Expression();

    public void ChangeDetected()
	{
        string equation = "";
        Variant result;

        foreach (var symbol in puzzleParts)
        {
            if (symbol is MathSignal transmitter)
            {
                equation += transmitter.GetValue();
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
