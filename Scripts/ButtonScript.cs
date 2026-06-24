using Godot;
using System;

public partial class ButtonScript : Node
{
	public override void _Ready()
    {

    }
    public void OnButtonPress()
	{
        SaveManager.Instance.TotalButtonClicks++;
        SaveManager.Instance.SavePlayerDataBinary();
        SaveManager.Instance.SavePlayerDataJson();
	}
}
