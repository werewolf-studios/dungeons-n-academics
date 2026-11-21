using Godot;
using System;

public partial class PlayerTurnState : CombatState
{
    [Export]
    public Button AttackButton { get; set; }

    [Export]
    public Button SpecialButton { get; set; }

    [Export]
    public Button ItemsButton { get; set; }

    [Export]
    public Button PlchldrButton2 { get; set; }

    [Export]
    public CombatPlayer player { get; set; }

    [Export]
    public ProgressBar playerHealthBar { get; set; }

    public override void Enter()
    {
        GD.Print("Entered PlayerTurnState");
        ShowButtons();
        AttackButton.CallDeferred(Control.MethodName.GrabFocus);
    }

    public override void Exit()
    {
        HideButtons();
    }

	private void OnAttackButtonPressed()
    {
        if (Combat != null) Combat.PendingAction = CombatMain.TurnAction.Attack;
        csm.TransitionTo("QuestionState");
    }

    private void OnSpecialButtonPressed()
    {
        if (Combat != null) Combat.PendingAction = CombatMain.TurnAction.Special;
        csm.TransitionTo("QuestionState");
    }

    private void OnItemsButtonPressed()
    {
        var menu = InventoryMenu.Instance;
        if (menu == null || menu.IsOpen) return;

        // Hide the command row so focus cannot escape the inventory while it is open.
        HideButtons();
        // Using an item does not spend the turn: close back to the command menu
        // and let the player still Attack or use Special.
        menu.OpenForBattle(player, _ => ShowButtons());
    }

    private void ShowButtons()
    {
        AttackButton.Show();
        SpecialButton.Show();
        ItemsButton.Show();
        PlchldrButton2.Show();
        playerHealthBar.Value = player.health;
    }

    private void HideButtons()
    {
        AttackButton.Hide();
        SpecialButton.Hide();
        ItemsButton.Hide();
        PlchldrButton2.Hide();
    }
}
