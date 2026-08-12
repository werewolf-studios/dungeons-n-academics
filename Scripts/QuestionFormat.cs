using Godot;
using System;
using System.ComponentModel.DataAnnotations;

public partial class QuestionFormat : Node
{
    public string ProblemFormat { get; set; }
    public string Min { get; set; }
    public string Max { get; set; }

    public QuestionFormat(string problemFormat, string min, string max)
    {
        ProblemFormat = problemFormat;
        Min = min;
        Max = max;
    }
}
