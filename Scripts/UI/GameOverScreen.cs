using Godot;
using System;

/// <summary>
/// Full-screen death screen shown when the player loses a battle. Retry reloads
/// the current level with a full health pool; Title returns to the main menu.
/// Uses the same focus/confirm/cancel conventions as the other menus.
/// </summary>
public partial class GameOverScreen : CanvasLayer
{
    public static GameOverScreen Instance { get; private set; }

    public bool IsOpen => Visible;

    private Button retry;
    private Button title;

    public override void _Ready()
    {
        Instance = this;
        ProcessMode = ProcessModeEnum.Always;

        retry = GetNode<Button>("Center/Margin/VBox/Retry");
        title = GetNode<Button>("Center/Margin/VBox/Title");
        retry.Pressed += OnRetry;
        title.Pressed += OnTitle;

        Visible = false;
    }

    public void Open()
    {
        if (Visible)
        {
            return;
        }
        Visible = true;
        GetTree().Paused = true;
        retry.CallDeferred(Control.MethodName.GrabFocus);
    }

    private void OnRetry()
    {
        // Retry restores the pool before reloading the level.
        SaveManager.Instance.PlayerData.ResetHealth();
        GetTree().Paused = false;
        Visible = false;
        GetViewport().GuiReleaseFocus();
        GetTree().ReloadCurrentScene();
    }

    private void OnTitle()
    {
        GetTree().Paused = false;
        Visible = false;
        GetViewport().GuiReleaseFocus();
        GetTree().ChangeSceneToFile("res://Scenes/menu.tscn");
    }
}
