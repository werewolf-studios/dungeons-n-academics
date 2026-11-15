using Godot;

/// <summary>
/// Autoload that gives every button in the game the same feel without per-scene setup:
/// a small "pop" when a button gains focus, a tick when the selection moves by
/// D-pad/stick/arrow input, and a confirm sound on press. Menus call Back() and
/// Pause() for the sounds only they know when to play. Runs while the game is paused.
/// </summary>
public partial class UiFeedback : Node
{
	public static UiFeedback Instance { get; private set; }

	private const string SoundDir = "res://Assets/Audio/UI/";
	private const float PopScale = 1.06f;
	private const float VolumeDb = -6f;

	private AudioStreamPlayer move;
	private AudioStreamPlayer confirm;
	private AudioStreamPlayer back;
	private AudioStreamPlayer pause;
	private long navigationFrame = -10;

	public override void _Ready()
	{
		Instance = this;
		ProcessMode = ProcessModeEnum.Always;
		move = AddPlayer("ui_move");
		confirm = AddPlayer("ui_confirm");
		back = AddPlayer("ui_back");
		pause = AddPlayer("ui_pause");

		GetTree().NodeAdded += OnNodeAdded;
		HookTree(GetTree().Root);
	}

	/// <summary>Name of the last sound played (for tests and debugging).</summary>
	public string LastSound { get; set; } = "";

	public void Back() => Play(back);
	public void Pause() => Play(pause);
	/// <summary>The move tick, for menus that change selection without moving focus (tabs, sliders).</summary>
	public void Tick() => Play(move);

	private void Play(AudioStreamPlayer player)
	{
		LastSound = player.Name;
		player.Play();
	}

	public override void _Input(InputEvent @event)
	{
		// Remember when the player navigated, so only input-driven focus changes tick.
		if (@event.IsActionPressed("ui_up") || @event.IsActionPressed("ui_down") ||
			@event.IsActionPressed("ui_left") || @event.IsActionPressed("ui_right") ||
			@event.IsActionPressed("ui_focus_next") || @event.IsActionPressed("ui_focus_prev"))
		{
			navigationFrame = (long)Engine.GetProcessFrames();
		}
	}

	private AudioStreamPlayer AddPlayer(string name)
	{
		var player = new AudioStreamPlayer { Name = name, VolumeDb = VolumeDb, MaxPolyphony = 2, Bus = "SFX" };
		string path = SoundDir + name + ".mp3";
		if (ResourceLoader.Exists(path)) player.Stream = GD.Load<AudioStream>(path);
		else GD.PushWarning("UiFeedback: missing " + path);
		AddChild(player);
		return player;
	}

	private void HookTree(Node node)
	{
		OnNodeAdded(node);
		foreach (Node child in node.GetChildren()) HookTree(child);
	}

	private void OnNodeAdded(Node node)
	{
		if (node is not BaseButton button || button.HasMeta("_ui_feedback")) return;
		button.SetMeta("_ui_feedback", true);
		button.FocusEntered += () => OnFocusEntered(button);
		button.FocusExited += () => SetPopped(button, false);
		button.Pressed += () => Play(confirm);
	}

	private void OnFocusEntered(BaseButton button)
	{
		if ((long)Engine.GetProcessFrames() - navigationFrame <= 1) Play(move);
		SetPopped(button, true);
	}

	private static void SetPopped(BaseButton button, bool popped)
	{
		if (!IsInstanceValid(button) || !button.IsInsideTree()) return;
		button.PivotOffset = button.Size / 2;
		// Drawn above neighbours while enlarged so the pop is never clipped by them.
		button.ZIndex = popped ? 1 : 0;
		var tween = button.CreateTween();
		tween.SetProcessMode(Tween.TweenProcessMode.Idle);
		tween.TweenProperty(button, "scale", Vector2.One * (popped ? PopScale : 1f), popped ? 0.12 : 0.08)
			.SetTrans(Tween.TransitionType.Back).SetEase(Tween.EaseType.Out);
	}
}
