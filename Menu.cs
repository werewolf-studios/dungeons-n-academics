using Godot;
using System.Text.RegularExpressions;

public partial class Menu : CanvasLayer
{
	[Export]
	public string levelPath = "res://Scenes/player_controller_test.tscn";
	
	// Connected to this node's ready signal in menu.tscn. Gamepad navigation needs a
	// focused button to start from.
	public void _on_ready()
	{
		GetNode<Button>("MainButtons/MarginContainer/VBoxContainer/Start Button").CallDeferred(Control.MethodName.GrabFocus);
	}

	public void _on_start_button_pressed()
	{
		GetTree().ChangeSceneToFile(levelPath);
	}

	private void OnSettingsPressed()
	{
		GetNode<VBoxContainer>("MainButtons/MarginContainer/VBoxContainer").Visible = false;
		//Change this later to texture rect for scroll design
		GetNode<ColorRect>("MainButtons/ColorRect").Visible = false;
		GetNode<TextureRect>("SettingsMenu").Visible = true;
		GetNode<Button>("SettingsMenu/HBoxContainer/Graphics").GrabFocus();
	}

	// B / Esc closes the settings screen.
	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event.IsActionPressed("ui_cancel") && GetNode<TextureRect>("SettingsMenu").Visible)
		{
			UiFeedback.Instance?.Back();
			OnClosePressed();
			GetViewport().SetInputAsHandled();
		}
	}

	private void OnQuitPressed()
	{
		GetTree().Quit();
	}

	private void OnGraphicsPressed()
	{
		GetNode<TextureRect>("SettingsMenu/HBoxContainer/Graphics/GraphicsSelection").Visible = true;
		if (GetNode<TextureRect>("SettingsMenu/HBoxContainer/Audio/AudioSelection").Visible == true)
		{
			GetNode<TextureRect>("SettingsMenu/HBoxContainer/Audio/AudioSelection").Visible = false;
		}
		if (GetNode<TextureRect>("SettingsMenu/HBoxContainer/Controls/ControlsSelection").Visible == true)
		{
			GetNode<TextureRect>("SettingsMenu/HBoxContainer/Controls/ControlsSelection").Visible = false;
		}
	}

	private void OnControlsPressed()
	{
		GetNode<TextureRect>("SettingsMenu/HBoxContainer/Controls/ControlsSelection").Visible = true;
		if (GetNode<TextureRect>("SettingsMenu/HBoxContainer/Audio/AudioSelection").Visible == true)
		{
			GetNode<TextureRect>("SettingsMenu/HBoxContainer/Audio/AudioSelection").Visible = false;
		}
		if (GetNode<TextureRect>("SettingsMenu/HBoxContainer/Graphics/GraphicsSelection").Visible == true)
		{
			GetNode<TextureRect>("SettingsMenu/HBoxContainer/Graphics/GraphicsSelection").Visible = false;
		}
	}

	private void OnAudioPressed()
	{
		GetNode<TextureRect>("SettingsMenu/HBoxContainer/Audio/AudioSelection").Visible = true;
		if (GetNode<TextureRect>("SettingsMenu/HBoxContainer/Controls/ControlsSelection").Visible == true)
		{
			GetNode<TextureRect>("SettingsMenu/HBoxContainer/Controls/ControlsSelection").Visible = false;
		}
		if (GetNode<TextureRect>("SettingsMenu/HBoxContainer/Graphics/GraphicsSelection").Visible == true)
		{
			GetNode<TextureRect>("SettingsMenu/HBoxContainer/Graphics/GraphicsSelection").Visible = false;
		}
	}

	private void OnClosePressed()
	{
		GetNode<TextureRect>("SettingsMenu").Visible = false;
		GetNode<VBoxContainer>("MainButtons/MarginContainer/VBoxContainer").Visible = true;
		//Change this later to texture rect for scroll design
		GetNode<ColorRect>("MainButtons/ColorRect").Visible = true;
		GetNode<Button>("MainButtons/MarginContainer/VBoxContainer/Settings Button").GrabFocus();
	}

}
