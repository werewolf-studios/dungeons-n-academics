using Godot;
using System;

/// <summary>
/// Autoloaded inventory menu shared by the dungeon and combat. Opens with Tab or
/// D-pad Up in the dungeon, or from the battle Items button. Godot focus handles
/// keyboard/controller navigation; rows are buttons so mouse clicks work too.
/// While open the scene tree is paused, so gameplay cannot run behind it.
/// </summary>
public partial class InventoryMenu : CanvasLayer
{
    public static InventoryMenu Instance { get; private set; }

    private Control center;
    private VBoxContainer list;
    private Label description;

    private bool open;
    private CombatPlayer battlePlayer;
    private Action<bool> finished;

    public bool IsOpen => open;

    public override void _Ready()
    {
        Instance = this;
        ProcessMode = ProcessModeEnum.Always;
        center = GetNode<Control>("Center");
        list = GetNode<VBoxContainer>("Center/Margin/VBox/Scroll/List");
        description = GetNode<Label>("Center/Margin/VBox/Description");
        Visible = false;
    }

    public override void _Input(InputEvent @event)
    {
        if (!open)
        {
            if (@event.IsActionPressed("OpenInventory") && CanOpen())
            {
                OpenForLevel();
                GetViewport().SetInputAsHandled();
            }
            return;
        }

        bool close = @event.IsActionPressed("ui_cancel");
        // Tab closes. D-pad Up opens the menu, so while open it must keep
        // navigating rows instead of toggling the menu shut.
        if (@event is InputEventKey key && key.Pressed && !key.Echo && key.Keycode == Key.Tab)
        {
            close = true;
        }

        if (close)
        {
            Close(false);
            GetViewport().SetInputAsHandled();
        }
    }

    /// <summary>Dungeon path: browse and use items outside of battle.</summary>
    public void OpenForLevel()
    {
        battlePlayer = null;
        finished = null;
        ShowMenu();
    }

    /// <summary>Battle path: uses heal the active combat player; the callback receives true when an item was used.</summary>
    public void OpenForBattle(CombatPlayer player, Action<bool> onFinished)
    {
        battlePlayer = player;
        finished = onFinished;
        ShowMenu();
    }

    private void ShowMenu()
    {
        Rebuild();
        Visible = true;
        open = true;
        GetTree().Paused = true;
        Input.MouseMode = Input.MouseModeEnum.Visible;

        if (list.GetChildCount() > 0 && list.GetChild(0) is Control first)
        {
            first.CallDeferred(Control.MethodName.GrabFocus);
        }
    }

    private void Close(bool usedItem)
    {
        if (!open) return;
        open = false;
        Visible = false;
        GetTree().Paused = false;
        // The confirm press must not also count as an overworld interact.
        Input.ActionRelease("AttackInteract");
        GetViewport().GuiReleaseFocus();

        var callback = finished;
        finished = null;
        battlePlayer = null;
        callback?.Invoke(usedItem);
    }

    private void Rebuild()
    {
        foreach (Node child in list.GetChildren())
        {
            list.RemoveChild(child);
            child.QueueFree();
        }

        bool any = false;
        foreach (var definition in ItemCatalog.All)
        {
            int count = SaveManager.Instance.PlayerData.GetItemCount(definition.Id);
            if (count <= 0) continue;

            any = true;
            string id = definition.Id;
            var button = new Button
            {
                Text = $"{definition.DisplayName}   x{count}",
                CustomMinimumSize = new Vector2(0, 46),
                FocusMode = Control.FocusModeEnum.All,
                Alignment = HorizontalAlignment.Left,
            };
            StyleRow(button);
            // Full-width list rows opt out of the global focus "pop": scaling them
            // inside the clipping list cuts the left edge of the highlighted label.
            // They still play the shared tick/confirm sounds below.
            button.SetMeta("_ui_feedback", true);
            button.Pressed += () =>
            {
                UiFeedback.Instance?.Confirm();
                UseItem(id);
            };
            button.FocusEntered += () =>
            {
                UiFeedback.Instance?.Tick();
                description.Text = definition.Description;
            };
            button.MouseEntered += button.GrabFocus;
            list.AddChild(button);
        }

        description.Text = any ? "" : "Your pack is empty.";
    }

    private static void StyleRow(Button button)
    {
        // Identical content margins on every state: the label must not shift when
        // focus swaps the stylebox (that shift was clipping the first letter).
        const float padX = 18f;
        const float padY = 6f;

        var normal = new StyleBoxFlat { BgColor = new Color(0.12f, 0.16f, 0.31f, 0.95f) };
        normal.SetCornerRadiusAll(6);
        var hover = new StyleBoxFlat { BgColor = new Color(0.17f, 0.22f, 0.40f, 0.95f) };
        hover.SetCornerRadiusAll(6);
        var focus = new StyleBoxFlat
        {
            BgColor = new Color(0.6f, 0.35f, 1f, 0.30f),
            BorderColor = new Color(0.72f, 0.45f, 1f, 1f),
        };
        focus.SetCornerRadiusAll(6);
        focus.SetBorderWidthAll(4);

        foreach (var style in new[] { normal, hover, focus })
        {
            style.ContentMarginLeft = padX;
            style.ContentMarginRight = padX;
            style.ContentMarginTop = padY;
            style.ContentMarginBottom = padY;
        }

        button.AddThemeFontSizeOverride("font_size", 24);
        button.AddThemeStyleboxOverride("normal", normal);
        button.AddThemeStyleboxOverride("hover", hover);
        button.AddThemeStyleboxOverride("pressed", hover);
        button.AddThemeStyleboxOverride("focus", focus);
        button.AddThemeColorOverride("font_color", Colors.White);
    }

    private void UseItem(string itemId)
    {
        var definition = ItemCatalog.Get(itemId);
        if (definition == null) return;

        if (definition.Heal <= 0)
        {
            ItemToast.Instance?.ShowMessage("Only usable in battle.");
            return;
        }

        var data = SaveManager.Instance.PlayerData;
        int healed;
        if (battlePlayer != null)
        {
            if (battlePlayer.health >= CombatPlayer.MaxHealth)
            {
                ItemToast.Instance?.ShowMessage("HP is already full.");
                return;
            }
            healed = battlePlayer.Heal(definition.Heal);
        }
        else
        {
            if (data.Health >= PlayerSaveData.MaxHealth)
            {
                ItemToast.Instance?.ShowMessage("HP is already full.");
                return;
            }
            healed = data.Heal(definition.Heal);
        }

        if (healed <= 0) return;

        data.ConsumeItem(itemId);
        ItemToast.Instance?.ShowMessage($"{definition.DisplayName} restored {healed} HP.");
        Close(true);
    }

    private bool CanOpen()
    {
        // A pause menu or another modal already owns the game.
        if (GetTree().Paused) return false;
        if (FindQuiz(GetTree().Root)) return false;
        // In battle the Items command owns this menu; Tab/D-pad must not open it.
        if (FindCombatMain(GetTree().CurrentScene) != null) return false;
        return true;
    }

    private static bool FindQuiz(Node node)
    {
        if (node is QuestionManager quiz && quiz.Visible) return true;
        foreach (Node child in node.GetChildren())
        {
            if (FindQuiz(child)) return true;
        }
        return false;
    }

    private static CombatMain FindCombatMain(Node node)
    {
        if (node == null) return null;
        if (node is CombatMain combat) return combat;
        foreach (Node child in node.GetChildren())
        {
            var found = FindCombatMain(child);
            if (found != null) return found;
        }
        return null;
    }
}
