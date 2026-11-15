using Godot;

public partial class Menu : CanvasLayer
{
	[Export]
	public string levelPath = "res://Scenes/player_controller_test.tscn";

	private const string MainButtonsBox = "MainButtons/MarginContainer/VBoxContainer";

	private SettingsPanel settings;

	public override void _Ready()
	{
		// The shared settings panel (also used by the pause menu) handles its own
		// tabs and B/Esc; when it closes, bring the main buttons back.
		settings = GetNode<SettingsPanel>("SettingsPanel");
		settings.Closed += OnSettingsClosed;
	}

	// Connected to this node's ready signal in menu.tscn. Gamepad navigation needs a
	// focused button to start from.
	public void _on_ready()
	{
		GetNode<Button>(MainButtonsBox + "/Start Button").CallDeferred(Control.MethodName.GrabFocus);
	}

	public void _on_start_button_pressed()
	{
		GetTree().ChangeSceneToFile(levelPath);
	}

	private void OnSettingsPressed()
	{
		SetMainButtonsVisible(false);
		settings.Open();
	}

	private void OnSettingsClosed()
	{
		SetMainButtonsVisible(true);
		GetNode<Button>(MainButtonsBox + "/Settings Button").GrabFocus();
	}

	private void OnQuitPressed()
	{
		GetTree().Quit();
	}

	private void SetMainButtonsVisible(bool visible)
	{
		GetNode<Control>(MainButtonsBox).Visible = visible;
		GetNode<ColorRect>("MainButtons/ColorRect").Visible = visible;
	}
}
