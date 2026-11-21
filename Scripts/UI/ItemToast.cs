using Godot;

/// <summary>
/// Autoloaded toast line for item pickups and item feedback. One message at a
/// time: a new message replaces the previous one and restarts the fade.
/// </summary>
public partial class ItemToast : CanvasLayer
{
    public static ItemToast Instance { get; private set; }

    private Label label;
    private Tween tween;

    public override void _Ready()
    {
        Instance = this;
        ProcessMode = ProcessModeEnum.Always;
        label = GetNode<Label>("Label");
        label.Modulate = new Color(1, 1, 1, 0);
    }

    public void ShowMessage(string message)
    {
        if (string.IsNullOrEmpty(message)) return;

        label.Text = message;
        tween?.Kill();
        label.Modulate = new Color(1, 1, 1, 0);

        // Stops immediately follow the previous message instead of queuing.
        tween = CreateTween();
        tween.TweenProperty(label, "modulate:a", 1.0f, 0.15f);
        tween.TweenInterval(1.6f);
        tween.TweenProperty(label, "modulate:a", 0.0f, 0.35f);
    }
}
