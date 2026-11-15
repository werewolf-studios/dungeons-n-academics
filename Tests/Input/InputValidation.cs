using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

/// <summary>
/// Drives the real Player, pause menu, combat scene and main menu with simulated
/// gamepad events (Input.ParseInputEvent), the same path a physical controller uses.
/// </summary>
public partial class InputValidation : Node3D
{
    private const string TestSettingsPath = "user://settings_test.cfg";
    private readonly List<string> passed = new();
    private PauseMenu pause;

    public override async void _Ready()
    {
        // The quiz awards/deducts coins and saves immediately; put the player's save back afterwards.
        SaveManager.Instance.LoadPlayerDataBinary();
        int savedCoins = SaveManager.Instance.PlayerData.Coins;
        int savedXp = SaveManager.Instance.PlayerData.XP;
        // Settings changes go to a throwaway file; the player's settings are reloaded afterwards.
        var settings = GameSettings.Instance;
        string realSettingsPath = settings.ConfigPath;
        settings.ConfigPath = TestSettingsPath;
        TreeExiting += () =>
        {
            SaveManager.Instance.PlayerData.Coins = savedCoins;
            SaveManager.Instance.PlayerData.XP = savedXp;
            DirAccess.RemoveAbsolute(ProjectSettings.GlobalizePath(TestSettingsPath));
            settings.ConfigPath = realSettingsPath;
            settings.Load();
            settings.ApplyAll();
        };
        try
        {
            pause = GetNode<PauseMenu>("/root/PauseMenu");
            await Overworld();
            await Combat();
            await MainMenu();
            GD.Print("INPUT_VALIDATION_PASS " + passed.Count + " checks");
            using var report = FileAccess.Open("res://Tests/Input/validation-results.txt", FileAccess.ModeFlags.Write);
            report.StoreString(string.Join("\n", passed));
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PrintErr("INPUT_VALIDATION_FAIL " + error.Message);
            GetTree().Paused = false;
            GetTree().Quit(1);
        }
    }

    // ---------------- Overworld + pause menu ----------------
    private async Task Overworld()
    {
        var floor = new StaticBody3D { Position = new Vector3(0, -0.5f, 0) };
        floor.AddChild(new CollisionShape3D { Shape = new BoxShape3D { Size = new Vector3(100, 1, 100) } });
        AddChild(floor);
        var player = GD.Load<PackedScene>("res://Scenes/player.tscn").Instantiate<Player>();
        player.Speed = 10;
        AddChild(player);
        var brother = player.GetNode<ExplorationCharacterVisual>("Pivot/Male-Character");
        await Physics(5);

        Axis(JoyAxis.LeftY, 1f);
        await Physics(8);
        Check(Mathf.IsEqualApprox(HorizontalSpeed(player), 10, 0.01f) && brother.CurrentClip == "Run", "full stick tilt runs at full speed");
        Axis(JoyAxis.LeftY, 0.5f);
        await Physics(8);
        Check(Mathf.IsEqualApprox(HorizontalSpeed(player), 10 * player.WalkSpeedRatio, 0.05f) && brother.CurrentClip == "Walk",
            "light stick tilt walks at walk speed");
        Axis(JoyAxis.LeftY, 0.1f);
        await Physics(8);
        Check(HorizontalSpeed(player) < 0.05f && brother.CurrentClip == "Idle", "stick inside the deadzone stays idle");
        Axis(JoyAxis.LeftY, 0f);
        Button(JoyButton.DpadDown, true);
        await Physics(8);
        Check(Mathf.IsEqualApprox(HorizontalSpeed(player), 10, 0.01f) && brother.CurrentClip == "Run", "D-pad moves at full speed");
        Button(JoyButton.DpadRight, true);
        await Physics(6);
        Check(Mathf.IsEqualApprox(HorizontalSpeed(player), 10, 0.01f), "D-pad diagonal stays normalized");
        Button(JoyButton.DpadRight, false);
        Button(JoyButton.LeftShoulder, true);
        await Physics(8);
        Check(brother.CurrentClip == "Walk" && HorizontalSpeed(player) < 4, "LB still forces walking");
        Button(JoyButton.LeftShoulder, false);

        // Pause while moving: everything freezes.
        await Tap(JoyButton.Start);
        Check(pause.IsOpen && GetTree().Paused, "Start opens the pause menu and pauses the game");
        await Frames(2);
        Check(Focused()?.Name == "Resume", "Resume has gamepad focus");
        var ui = UiFeedback.Instance;
        Check(ui.LastSound == "ui_pause", "opening the pause menu plays the pause sound, not a move tick");
        Vector3 frozenAt = player.Position;
        await Physics(15);
        Check(player.Position.IsEqualApprox(frozenAt), "player is frozen while paused");
        var resume = (Control)Focused();
        Check(resume.Scale.X > 1.03f && Mathf.IsEqualApprox(GetNode<Control>("/root/PauseMenu/Center").Modulate.A, 1f),
            "pause menu has faded in and the focused button pops");
        Button(JoyButton.DpadDown, false);
        await Tap(JoyButton.DpadDown);
        Check(Focused()?.Name == "Settings" && ui.LastSound == "ui_move", "D-pad moves focus in the pause menu with a tick");
        await Frames(10);
        Check(Mathf.IsEqualApprox(resume.Scale.X, 1f), "the previous button shrinks back");

        // Settings from the pause menu: tabs, a volume slider, saving, B back.
        var panel = GetNode<SettingsPanel>("/root/PauseMenu/SettingsPanel");
        await Tap(JoyButton.A);
        await Frames(2);
        Check(panel.Visible && Focused()?.Name == "Graphics" && ui.LastSound == "ui_confirm",
            "A opens settings on the Graphics tab with a confirm sound");
        await Tap(JoyButton.RightShoulder);
        await Frames(2);
        Check(Focused()?.Name == "Audio" && panel.GetNode<Control>("Center/Panel/Margin/VBox/Pages/AudioPage").Visible,
            "RB switches to the Audio tab");
        await Tap(JoyButton.DpadDown);
        Check(Focused()?.Name == "Master", "D-pad down reaches the first option");
        var masterRow = panel.GetNode<PanelContainer>("Center/Panel/Margin/VBox/Pages/AudioPage/MasterRow");
        Check(masterRow.ThemeTypeVariation == "SettingsRowFocused", "the focused option's row is highlighted");
        float masterBefore = GameSettings.Instance.MasterVolume;
        await Tap(JoyButton.DpadLeft);
        float expected = Mathf.Max(masterBefore - 0.05f, 0f);
        int masterBus = AudioServer.GetBusIndex("Master");
        Check(Mathf.IsEqualApprox(GameSettings.Instance.MasterVolume, expected, 0.001f)
            && Mathf.IsEqualApprox(AudioServer.GetBusVolumeDb(masterBus), Mathf.LinearToDb(expected), 0.01f),
            "D-pad left lowers master volume by 5% and applies it to the bus");
        var saved = new ConfigFile();
        Check(saved.Load(TestSettingsPath) == Error.Ok && Mathf.IsEqualApprox((float)saved.GetValue("audio", "master"), expected, 0.001f),
            "the change is saved (to the test settings file)");
        await Tap(JoyButton.LeftShoulder);
        await Tap(JoyButton.LeftShoulder);
        Check(Focused()?.Name == "Controls" && panel.GetNode<Control>("Center/Panel/Margin/VBox/Pages/ControlsPage").Visible,
            "LB wraps round to the Controls tab");
        await Tap(JoyButton.B);
        await Frames(2);
        Check(pause.IsOpen && !panel.Visible && Focused()?.Name == "Settings" && ui.LastSound == "ui_back",
            "B leaves settings back to the pause menu with a back sound");
        await Tap(JoyButton.B);
        Check(!pause.IsOpen && !GetTree().Paused, "B closes the pause menu");

        // Resume with A: the held A must not fire an interaction.
        var interact = GD.Load<PackedScene>("res://Scenes/interaction_test.tscn").Instantiate<InteractionTest>();
        interact.Position = new Vector3(0, 1, -1.1f);
        player.Position = Vector3.Zero;
        player.GetNode<Node3D>("Pivot").Basis = Basis.LookingAt(Vector3.Forward);
        AddChild(interact);
        await Physics(5);
        var mesh = interact.GetNode<MeshInstance3D>("MeshInstance3D");
        var material = mesh.MaterialOverride;
        await Tap(JoyButton.Start);
        await Frames(2);
        Button(JoyButton.A, true); // buttons fire on release, so holding A keeps the menu open
        await Frames(2);
        Check(pause.IsOpen, "holding A on Resume waits for release");
        Button(JoyButton.A, false);
        await Frames(2);
        Check(!pause.IsOpen && !GetTree().Paused, "releasing A on Resume resumes the game");
        await Physics(6);
        Check(mesh.MaterialOverride == material, "the A press that resumed does not trigger an interaction");
        await Tap(JoyButton.A);
        await Physics(3);
        Check(mesh.MaterialOverride != material, "A interacts in the overworld");
        material = mesh.MaterialOverride;
        await Tap(JoyButton.X);
        await Physics(3);
        Check(mesh.MaterialOverride != material, "X still interacts");
        interact.QueueFree();

        await Tap(JoyButton.Y);
        await Physics(3);
        Check(!player.IsCharacterMale, "Y swaps character");
        await Tap(JoyButton.Y);
        player.QueueFree();
        floor.QueueFree();
        await Physics(3);
    }

    // ---------------- Combat turn + quiz with a gamepad ----------------
    private async Task Combat()
    {
        UiFeedback.Instance.LastSound = "";
        var combat = GD.Load<PackedScene>("res://Scenes/CombatSystem/combat_main.tscn").Instantiate<CombatMain>();
        AddChild(combat);
        await Frames(4);
        var csm = combat.GetNode<CombatStateMachine>("CombatStateMachine");
        Check(Focused()?.Name == "AttackButton", "player turn starts with focus on Attack");
        Check(UiFeedback.Instance.LastSound == "", "a menu taking focus on its own makes no sound");
        await Tap(JoyButton.A);
        await Frames(4);
        var quiz = combat.GetNode<QuestionManager>("Main/QuestionsUI");
        Check(csm.CurrentState.Name == "QuestionState" && quiz.Visible, "A on Attack opens the quiz");
        var answers = quiz.GetNode<Control>("Control/VBoxContainer");
        Check(Focused() == answers.GetChild(0), "quiz starts with focus on the first answer");
        await Tap(JoyButton.DpadDown);
        Check(Focused() == answers.GetChild(1), "D-pad moves between answers");

        var countdown = quiz.GetNode<Timer>("Control/Timer");
        await Tap(JoyButton.Start);
        double timeLeft = countdown.TimeLeft;
        await Seconds(1.5);
        Check(Mathf.IsEqualApprox(countdown.TimeLeft, timeLeft), "the question countdown stops while paused");
        await Tap(JoyButton.Start);
        await Frames(2);
        Check(Focused() == answers.GetChild(1), "resuming returns focus to the same answer");

        bool answered = false;
        quiz.AnswerDisplayed += () => answered = true;
        await Tap(JoyButton.A);
        Check(answered && Focused() == null, "A answers; focus is released during the reveal");
        await Tap(JoyButton.A);
        Check(csm.CurrentState.Name == "QuestionState", "presses during the reveal do nothing");

        await Tap(JoyButton.Start);
        await Seconds(6); // longer than the 5 s reveal (and the 0.15 s fade-in)
        Check(pause.IsOpen && Mathf.IsEqualApprox(GetNode<ColorRect>("/root/PauseMenu/Dim").Color.A, 1f),
            "pausing during the quiz covers it completely");
        Check(csm.CurrentState.Name == "QuestionState" && quiz.Visible, "the answer reveal waits while paused");
        await Tap(JoyButton.Start);
        Check(!GetTree().Paused, "Start resumes");
        await Until(() => csm.CurrentState.Name != "QuestionState", 7, "quiz finishes after resuming");
        combat.QueueFree();
        await Frames(3);
    }

    // ---------------- Main menu ----------------
    private async Task MainMenu()
    {
        // ChangeSceneToFile would free this test, so load the menu beside it as the current scene.
        var menu = GD.Load<PackedScene>("res://Scenes/menu.tscn").Instantiate();
        GetTree().Root.AddChild(menu);
        GetTree().CurrentScene = menu;
        await Frames(6);
        Check(Focused()?.Name == "Start Button", "main menu starts with focus on Start Game");
        await Tap(JoyButton.Start);
        Check(!pause.IsOpen && !GetTree().Paused, "Start does not pause on the main menu");
        await Tap(JoyButton.DpadDown);
        Check(Focused()?.Name == "Settings Button", "D-pad moves through the main menu");
        await Tap(JoyButton.A);
        await Frames(2);
        var panel = menu.GetNode<SettingsPanel>("SettingsPanel");
        Check(panel.Visible && Focused()?.Name == "Graphics" && !menu.GetNode<Control>("MainButtons/ColorRect").Visible,
            "A opens the shared settings panel in place of the main buttons");
        await Tap(JoyButton.DpadDown);
        Check(Focused()?.Name == "DisplayMode", "D-pad down reaches Display Mode");
        Check(menu.GetNode<AudioStreamPlayer>("MenuMusic").Bus == "Music", "menu music player is routed to the Music bus");
        await Tap(JoyButton.B);
        await Frames(2);
        Check(!panel.Visible && Focused()?.Name == "Settings Button", "B closes settings");
    }

    // ---------------- helpers ----------------
    private static void Button(JoyButton button, bool pressed) =>
        Input.ParseInputEvent(new InputEventJoypadButton { Device = 0, ButtonIndex = button, Pressed = pressed });

    private static void Axis(JoyAxis axis, float value) =>
        Input.ParseInputEvent(new InputEventJoypadMotion { Device = 0, Axis = axis, AxisValue = value });

    private async Task Tap(JoyButton button)
    {
        // Hold across physics frames: Player reads actions in _PhysicsProcess.
        Button(button, true);
        await Physics(2);
        Button(button, false);
        await Physics(2);
    }

    private Control Focused() => GetViewport().GuiGetFocusOwner();

    private static float HorizontalSpeed(Player p) => new Vector2(p.GetRealVelocity().X, p.GetRealVelocity().Z).Length();

    private async Task Frames(int count)
    {
        for (int i = 0; i < count; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
    }

    private async Task Physics(int count)
    {
        for (int i = 0; i < count; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
    }

    private async Task Seconds(double seconds) =>
        await ToSignal(GetTree().CreateTimer(seconds, true), SceneTreeTimer.SignalName.Timeout);

    private async Task Until(Func<bool> condition, double timeout, string message)
    {
        double end = Time.GetTicksMsec() / 1000.0 + timeout;
        while (!condition())
        {
            if (Time.GetTicksMsec() / 1000.0 > end) throw new Exception("timed out: " + message);
            await Frames(1);
        }
        Check(true, message);
    }

    private void Check(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
        passed.Add("PASS " + message);
        GD.Print(passed[^1]);
    }
}
