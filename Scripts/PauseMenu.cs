using Godot;

/// <summary>
/// Autoloaded pause menu (Scenes/UI/pause_menu.tscn). Lives outside the level so
/// SceneManager's battle idle logic never changes its process mode. Runs while the
/// tree is paused (ProcessMode Always on the scene root).
/// </summary>
public partial class PauseMenu : CanvasLayer
{
	private const string MainMenuScene = "res://Scenes/menu.tscn";

	public bool IsOpen => Visible;

	private ColorRect dim;
	private Control mainPage;
	private Control controlsPage;
	private Button resumeButton;
	private Button controlsButton;
	private Control focusBeforePause;

	public override void _Ready()
	{
		dim = GetNode<ColorRect>("Dim");
		mainPage = GetNode<Control>("Center/Panel/Margin/MainPage");
		controlsPage = GetNode<Control>("Center/Panel/Margin/ControlsPage");
		resumeButton = mainPage.GetNode<Button>("Resume");
		controlsButton = mainPage.GetNode<Button>("Controls");

		resumeButton.Pressed += Close;
		controlsButton.Pressed += ShowControls;
		mainPage.GetNode<Button>("MainMenu").Pressed += GoToMainMenu;
		mainPage.GetNode<Button>("Quit").Pressed += () => GetTree().Quit();
		controlsPage.GetNode<Button>("Back").Pressed += ShowMain;

		Visible = false;
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (IsOpen)
		{
			// Start/Esc closes; B goes back from the controls page, otherwise closes.
			bool pause = @event.IsActionPressed("Pause");
			if (pause || @event.IsActionPressed("ui_cancel"))
			{
				UiFeedback.Instance?.Back();
				if (!pause && controlsPage.Visible) ShowMain();
				else Close();
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
		ShowMain();
		Visible = true;
		GetTree().Paused = true;
		UiFeedback.Instance?.Pause();

		// Quick fade in; the menu is usable immediately.
		var center = GetNode<Control>("Center");
		dim.Color = new Color(0, 0, 0, 0);
		center.Modulate = new Color(1, 1, 1, 0);
		fade?.Kill();
		fade = CreateTween().SetParallel();
		fade.TweenProperty(dim, "color:a", dimAlpha, 0.15);
		fade.TweenProperty(center, "modulate:a", 1.0f, 0.15);
	}

	private Tween fade;

	public void Close()
	{
		if (!IsOpen) return;
		fade?.Kill();
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

	private bool CanPause()
	{
		Node scene = GetTree().CurrentScene;
		return scene != null && scene.SceneFilePath != MainMenuScene;
	}

	// Opening focuses Resume; coming back from the controls page focuses Controls.
	private void ShowMain()
	{
		bool fromControls = controlsPage.Visible;
		controlsPage.Visible = false;
		mainPage.Visible = true;
		(fromControls ? controlsButton : resumeButton).CallDeferred(Control.MethodName.GrabFocus);
	}

	private void ShowControls()
	{
		mainPage.Visible = false;
		controlsPage.Visible = true;
		controlsPage.GetNode<Button>("Back").CallDeferred(Control.MethodName.GrabFocus);
	}

	private void GoToMainMenu()
	{
		Visible = false;
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
