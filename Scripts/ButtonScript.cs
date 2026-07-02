using Godot;
using System;

public partial class ButtonScript : Node
{
    [Export]
    public Label Label { get; set; }

    [Export]
    public Label QuestionLabel { get; set; }
    public override void _Ready()
    {
        SaveManager.Instance.LoadPlayerDataBinary();
        Label.Text = "Total Button Clicks: " + SaveManager.Instance.TotalButtonClicks;

        SaveManager.Instance.LoadQuestionDataJson();
        QuestionLabel.Text = SaveManager.Instance.Questions["math"][0].ToString();
    }
    public void OnButtonPress()
	{
        SaveManager.Instance.TotalButtonClicks++;
        SaveManager.Instance.SavePlayerDataBinary();
        SaveManager.Instance.SavePlayerDataJson();
        Label.Text = "Total Button Clicks: " + SaveManager.Instance.TotalButtonClicks;
    }
}
