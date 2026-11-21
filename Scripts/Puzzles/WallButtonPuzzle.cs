using Godot;
using System;
using System.Collections.Generic;

/// <summary>
/// Wall-button sum puzzle. An equation is drawn on the wall and the player
/// toggles numbered wall buttons until the selected values add up to its answer.
/// Solving unlocks the configured doors; overshooting clears the selection.
/// </summary>
public partial class WallButtonPuzzle : Node3D
{
    [Export] public Label3D EquationLabel { get; set; }
    [Export] public Label3D TotalLabel { get; set; }
    [Export] public string JsonPath { get; set; } = PuzzleEquationBank.DefaultPath;
    [Export] public string Category { get; set; } = "wall_sum";
    [Export] public Door[] DoorsToUnlock { get; set; } = Array.Empty<Door>();

    public bool IsSolved { get; private set; }
    public int Answer { get; private set; }
    public int RunningTotal { get; private set; }

    private readonly List<WallNumberButton> buttons = new();
    private string equationText = "? + ? = ?";
    private bool resetting;
    private SceneTreeTimer resetTimer;

    public override void _Ready()
    {
        foreach (Node child in GetChildren())
        {
            if (child is WallNumberButton button)
            {
                buttons.Add(button);
                button.SetPuzzle(this);
            }
        }

        var entry = PuzzleEquationBank.Roll(JsonPath, Category);
        if (entry != null)
        {
            equationText = entry.Text;
            Answer = entry.Answer;
        }
        else
        {
            GD.PushError("WallButtonPuzzle: could not load an equation; puzzle disabled.");
        }

        if (EquationLabel != null)
        {
            EquationLabel.Text = equationText;
            EquationLabel.Modulate = Colors.White;
        }
        UpdateTotal();
    }

    /// <summary>Called by a wall button when the player interacts with it.</summary>
    public void Toggle(WallNumberButton button)
    {
        if (IsSolved || resetting || button == null)
        {
            return;
        }

        if (button.Selected)
        {
            button.SetSelected(false);
            RunningTotal -= button.Value;
            UpdateTotal();
            return;
        }

        if (RunningTotal + button.Value > Answer)
        {
            Overshoot();
            return;
        }

        button.SetSelected(true);
        RunningTotal += button.Value;
        UpdateTotal();

        if (RunningTotal == Answer)
        {
            Solve();
        }
    }

    private void Overshoot()
    {
        // Overshooting is not a mistake to remember: clear the selection and
        // let the player start again.
        resetting = true;
        ResetSelection();

        if (TotalLabel != null)
        {
            TotalLabel.Text = "Too high!";
            TotalLabel.Modulate = new Color(1f, 0.25f, 0.2f, 1f);
        }

        if (resetTimer != null)
        {
            resetTimer.Timeout -= OnResetTimerTimeout;
        }
        resetTimer = GetTree().CreateTimer(0.8);
        resetTimer.Timeout += OnResetTimerTimeout;
    }

    private void OnResetTimerTimeout()
    {
        if (!IsInstanceValid(this) || IsSolved)
        {
            return;
        }
        resetting = false;
        UpdateTotal();
    }

    private void ResetSelection()
    {
        RunningTotal = 0;
        foreach (WallNumberButton button in buttons)
        {
            button.SetSelected(false);
        }
    }

    private void Solve()
    {
        IsSolved = true;
        if (EquationLabel != null)
        {
            EquationLabel.Text = equationText;
            EquationLabel.Modulate = new Color(0.25f, 1f, 0.35f, 1f);
        }
        if (TotalLabel != null)
        {
            TotalLabel.Text = "Correct!";
            TotalLabel.Modulate = new Color(0.25f, 1f, 0.35f, 1f);
        }

        foreach (Door door in DoorsToUnlock)
        {
            door?.Unlock();
        }
    }

    private void UpdateTotal()
    {
        if (TotalLabel == null)
        {
            return;
        }
        TotalLabel.Text = $"Selected: {RunningTotal}";
        TotalLabel.Modulate = Colors.White;
    }
}
