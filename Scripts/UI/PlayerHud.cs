using Godot;

/// <summary>
/// Persistent overworld health readout. Reads the shared health pool from
/// PlayerSaveData and follows its HealthChanged signal, including battle damage.
/// </summary>
public partial class PlayerHud : CanvasLayer
{
    private ProgressBar bar;
    private Label label;

    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always;
        bar = GetNode<ProgressBar>("Bar");
        label = GetNode<Label>("Bar/Label");

        PlayerSaveData data = SaveManager.Instance.PlayerData;
        data.HealthChanged += OnHealthChanged;
        UpdateHud(data.Health);
        Visible = ShouldShow();
    }

    public override void _Process(double delta)
    {
        bool show = ShouldShow();
        if (Visible != show)
        {
            Visible = show;
        }
    }

    /// <summary>The HUD belongs to exploration only: hidden in menus and in battle.</summary>
    private bool ShouldShow()
    {
        if (GameOverScreen.Instance != null && GameOverScreen.Instance.IsOpen)
        {
            return false;
        }
        Node scene = GetTree().CurrentScene;
        if (scene == null || scene.SceneFilePath == "res://Scenes/menu.tscn")
        {
            return false;
        }
        return !HasCombatMain(scene);
    }

    private static bool HasCombatMain(Node node)
    {
        if (node is CombatMain)
        {
            return true;
        }
        foreach (Node child in node.GetChildren())
        {
            if (HasCombatMain(child))
            {
                return true;
            }
        }
        return false;
    }

    private void OnHealthChanged(int health) => UpdateHud(health);

    private void UpdateHud(int health)
    {
        int max = PlayerSaveData.MaxHealth;
        bar.MaxValue = max;
        bar.Value = health;
        label.Text = $"HP {health} / {max}";
    }
}
