using Godot;
using System;
using System.Linq;

public partial class GrowingEquationManager : Node
{
    private string equation = "";
    private int statuesHit = 0;
    private int statueCount;
    private bool streak;

    private Expression _expression = new Expression();

    [Export]
    private int startNumber, resultNumber;
    [Export]
    private string[] equations = new string[4];
    private GrowingEquationPart[] children;

    public override void _Ready()
    {
        foreach (object childCheck in GetChildren())
        {
            if (childCheck is GrowingEquationPart)
            {
                statueCount++;
            }
        }

        equation = startNumber + equations[0];
        GD.Print(equation);
        GetNode<Label3D>("Text").Text = equation;

        children = new GrowingEquationPart[statueCount];

        int i = 0;
        foreach (object childCheck in GetChildren())
        {
            if (childCheck is GrowingEquationPart child)
            {
                children[i] = child;
                i++;
            }
        }

        streak = true;
    }

    public void DeviceHit(string value)
    {
        GD.Print("Correct: " + CheckAnswer());
        GD.Print("Input: " + value);
        if (CheckAnswer().ToString() != value)
        {
            GD.Print("Break");
            streak = false;
        }
        // Increment progress
        statuesHit++;

        if (statuesHit >= statueCount)
        {
            // All phases hit
            if (streak)
            {
                // All nodes hit correctly
                GetNode<Label3D>("Text").Text = "Correct";
                GetNode<Label3D>("Text").Modulate = new Color(0.0f, 1.0f, 0.0f, 1.0f);
            }
            else
            {
                // Order was incorrect
                GetNode<Label3D>("Text").Text = "Incorrect";
                GetNode<Label3D>("Text").Modulate = new Color(1.0f, 0.0f, 0.0f, 1.0f);
            }

            // Reset sequence
            equation = startNumber + equations[0];
            statuesHit = 0;
            GD.Print("Reset");

            foreach (GrowingEquationPart child in children)
            {
                child.Reset();
            }
        }
        else
        {
            // Array limit not reached
            GD.Print("Next");
            equation = value + equations[statuesHit];
            GD.Print(equation);

            // Show next options
            foreach (GrowingEquationPart child in children)
            {
                child.IncrementQuestion();
            }

            GetNode<Label3D>("Text").Text = equations[statuesHit].ToString();
        }
    }

	public float CheckAnswer()
	{
        Variant result;

        GD.Print("Calculating");
        GD.Print(equation);

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

                return resultNum;
            }
        }
        else
        {
            // Error fallback
            GetNode<Label3D>("Text").Text = "Error";
            GetNode<Label3D>("Text").Modulate = new Color(1.0f, 0.0f, 0.0f, 1.0f);
        }

        return 0;
    }
}
