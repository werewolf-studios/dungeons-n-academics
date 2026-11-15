using Godot;

/// <summary>
/// Ends the demo: when the player walks into this area, the screen fades to black and
/// the main menu loads. If a door is assigned, the area only works once that door is open.
/// </summary>
public partial class DemoEndTrigger : Area3D
{
    [Export]
    public Door requiredDoor;

    [Export(PropertyHint.File, "*.tscn")]
    public string menuScene = "res://Scenes/menu.tscn";

    [Export]
    public float fadeDuration = 1.2f;

    private bool ending;

    public override void _Ready()
    {
        BodyEntered += OnBodyEntered;
    }

    private void OnBodyEntered(Node3D body)
    {
        if (ending || body is not Player)
        {
            return;
        }
        if (requiredDoor != null && !requiredDoor.IsOpen)
        {
            return;
        }

        ending = true;

        // Fade to black on top of everything, then hand over to the main menu.
        CanvasLayer layer = new CanvasLayer { Layer = 128 };
        ColorRect fade = new ColorRect
        {
            Color = new Color(0, 0, 0, 0),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        fade.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        layer.AddChild(fade);
        GetTree().Root.AddChild(layer);

        // The layer lives under the root, so it survives the scene change and fades the menu in.
        SceneTree tree = GetTree();
        string target = menuScene;
        Tween tween = layer.CreateTween();
        tween.SetPauseMode(Tween.TweenPauseMode.Process);
        tween.TweenProperty(fade, "color:a", 1.0f, fadeDuration);
        tween.TweenCallback(Callable.From(() =>
        {
            tree.Paused = false;
            tree.ChangeSceneToFile(target);
        }));
        tween.TweenInterval(0.15f);
        tween.TweenProperty(fade, "color:a", 0.0f, 0.6f);
        tween.TweenCallback(Callable.From(layer.QueueFree));
    }
}
