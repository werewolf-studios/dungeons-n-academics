using Godot;

/// <summary>
/// Autoloaded pause menu (Scenes/UI/pause_menu.tscn). Lives outside the level so
/// SceneManager's battle idle logic never changes its process mode. Runs while the
/// tree is paused (ProcessMode Always on the scene root). Settings opens the shared
/// SettingsPanel, which handles its own B/Esc.
/// </summary>
public partial class PauseMenu : CanvasLayer
{
	private const string MainMenuScene = "res://Scenes/menu.tscn";

	public bool IsOpen => Visible;

	private ColorRect dim;
	private Control center;
	private Button resumeButton;
	private Button settingsButton;
	private SettingsPanel settings;
	private Control focusBeforePause;
	private Tween fade;

	public override void _Ready()
	{
		dim = GetNode<ColorRect>("Dim");
		center = GetNode<Control>("Center");
		var mainPage = center.GetNode<Control>("Panel/Margin/MainPage");
		resumeButton = mainPage.GetNode<Button>("Resume");
		settingsButton = mainPage.GetNode<Button>("Settings");
		settings = GetNode<SettingsPanel>("SettingsPanel");

		resumeButton.Pressed += Close;
		settingsButton.Pressed += OpenSettings;
		mainPage.GetNode<Button>("MainMenu").Pressed += GoToMainMenu;
		mainPage.GetNode<Button>("Quit").Pressed += () => GetTree().Quit();
		settings.Closed += () =>
		{
			center.Visible = true;
			settingsButton.CallDeferred(Control.MethodName.GrabFocus);
		};

		Visible = false;
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (IsOpen)
		{
			// Start always closes everything. B/Esc closes the pause menu; while the
			// settings panel is open it handles B/Esc itself (it receives input first).
			bool pause = @event.IsActionPressed("Pause");
			if (pause || (!settings.Visible && @event.IsActionPressed("ui_cancel")))
			{
				UiFeedback.Instance?.Back();
				Close();
				GetViewport().SetInputAsHandled();
			}
		}
		else if (@event.IsActionPressed("Pause") && CanPause())
		{
			Open();
			GetViewport().SetInputAsHandled();
		}
	}

	public void Open()
	{
		if (IsOpen) return;
		focusBeforePause = GetViewport().GuiGetFocusOwner();
		// Cover an active quiz completely so pausing can't buy thinking time.
		float dimAlpha = QuizIsVisible(GetTree().Root) ? 1.0f : 0.75f;
		settings.Visible = false;
		center.Visible = true;
		Visible = true;
		GetTree().Paused = true;
		UiFeedback.Instance?.Pause();
		resumeButton.CallDeferred(Control.MethodName.GrabFocus);

		// Quick fade in; the menu is usable immediately.
		dim.Color = new Color(0, 0, 0, 0);
		center.Modulate = new Color(1, 1, 1, 0);
		fade?.Kill();
		fade = CreateTween().SetParallel();
		fade.TweenProperty(dim, "color:a", dimAlpha, 0.15);
		fade.TweenProperty(center, "modulate:a", 1.0f, 0.15);
	}

	public void Close()
	{
		if (!IsOpen) return;
		fade?.Kill();
		settings.Visible = false;
		Visible = false;
		GetTree().Paused = false;
		// The A press that chose Resume must not count as an interact when play resumes.
		Input.ActionRelease("AttackInteract");
		if (IsInstanceValid(focusBeforePause) && focusBeforePause.IsVisibleInTree())
			focusBeforePause.GrabFocus();
		else
			GetViewport().GuiReleaseFocus();
		focusBeforePause = null;
	}

	private void OpenSettings()
	{
		center.Visible = false;
		settings.Open();
	}

	private bool CanPause()
	{
		Node scene = GetTree().CurrentScene;
		return scene != null && scene.SceneFilePath != MainMenuScene;
	}

	private void GoToMainMenu()
	{
		Visible = false;
		settings.Visible = false;
		GetTree().Paused = false;
		focusBeforePause = null;
		GetTree().ChangeSceneToFile(MainMenuScene);
	}

	private static bool QuizIsVisible(Node node)
	{
		if (node is QuestionManager quiz && quiz.Visible) return true;
		foreach (Node child in node.GetChildren())
			if (QuizIsVisible(child)) return true;
		return false;
	}
}
