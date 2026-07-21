using Godot;
using System.Text.RegularExpressions;

public partial class Menu : CanvasLayer
{
	private void OnSettingsPressed()
	{
		GetNode<VBoxContainer>("MainButtons/MarginContainer/VBoxContainer").Visible = false;
		//Change this later to texture rect for scroll design
		GetNode<ColorRect>("MainButtons/ColorRect").Visible = false;
		GetNode<TextureRect>("SettingsMenu").Visible = true;
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
	}

}
