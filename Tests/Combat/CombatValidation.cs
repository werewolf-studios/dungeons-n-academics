using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

/// <summary>
/// Drives the real combat_main.tscn through attack, hurt and defeat for both siblings.
/// Headless runs only check; rendered runs also save review captures beside this file.
/// </summary>
public partial class CombatValidation : Node
{
    private readonly List<string> passed = new();
    private bool capture;

    public override async void _Ready()
    {
        try
        {
            capture = DisplayServer.GetName() != "headless";

            // ---- Brother: idle, sword swing, flinch ----
            var (combat, player, csm, enemy) = await SpawnBattle(isMale: true);
            var brother = player.GetNode<CombatCharacterVisual>("Male-Character");
            var sister = player.GetNode<CombatCharacterVisual>("Female-Character");
            Check(brother.Visible && !sister.Visible && player.ActiveVisual == brother, "brother selected from overworld choice");
            Check(player.GetNodeOrNull("MeshInstance3D") == null && combat.FindChild("Male-Character", true, false) is CombatCharacterVisual,
                "temporary meshes replaced by animated v10 siblings");
            foreach (var actor in new[] { brother, sister })
            {
                Check(actor.AnimationTree.Active && actor.CurrentState == "Idle", actor.CharacterId + " starts in Idle");
                Check(!actor.SwordSocket.Visible && !actor.SpearSocket.Visible, actor.CharacterId + " weapons hidden while idle");
            }
            Vector3 toEnemy = (enemy.GlobalPosition - player.GlobalPosition) with { Y = 0 };
            Check(brother.GetNode<Node3D>("Model").GlobalBasis.Z.Normalized().Dot(toEnemy.Normalized()) > .99f, "brother faces the enemy");
            Check(sister.GetNode<Node3D>("Model").GlobalBasis.Z.Normalized().Dot(toEnemy.Normalized()) > .99f, "sister faces the enemy");
            await Seconds(3.4);
            Check(brother.CurrentState == "Idle" && brother.AnimationTree.IsActive(), "Idle keeps looping past its 3 s length");
            await Capture("combat-brother-idle");

            int enemyHealth = enemy.health;
            double hitPosition = -1;
            int hits = 0;
            player.AttackHit += () => { hits++; hitPosition = Playback(brother).GetCurrentPlayPosition(); };
            csm.TransitionTo("PlayerAttackState");
            await Until(() => brother.CurrentState == "SwordSlash", 1, "brother enters SwordSlash");
            Check(brother.SwordSocket.Visible && !brother.SpearSocket.Visible, "sword in hand during the swing");
            Check(sister.CurrentState == "Idle", "hidden sister does not swing");
            Check(enemy.health == enemyHealth, "no damage before the blade connects");
            await Until(() => hits > 0, 2, "swing reaches its contact frame");
            await Capture("combat-brother-slash-hit");
            Check(hitPosition >= .75 && hitPosition < .8, $"hit fires on SwordSlash frame 19 (0.75 s), got {hitPosition:0.000}");
            Check(enemy.health == enemyHealth - player.Damage, "enemy takes player damage on the hit");
            await Until(() => brother.CurrentState == "Idle", 2, "brother returns to Idle after the swing");
            Check(!brother.SwordSocket.Visible, "sword put away back in Idle");
            Check(!(bool)brother.AnimationTree.Get("parameters/conditions/attack"), "attack condition cleared");
            Check(hits == 1, "one hit per swing");

            // PAttkEndTimer hands over to the enemy, whose hit makes the brother flinch.
            int playerHealth = player.health;
            await Until(() => brother.CurrentState == "TakeDamage", 6, "enemy attack triggers brother TakeDamage");
            Check(player.health == playerHealth - 5, "player takes enemy damage as the flinch starts");
            await Seconds(.2);
            await Capture("combat-brother-hurt");
            await Until(() => brother.CurrentState == "Idle", 2.5, "brother reverts to Idle after TakeDamage");
            Check(!(bool)brother.AnimationTree.Get("parameters/conditions/hurt"), "hurt condition cleared");
            await Until(() => IsState(csm, "PlayerTurnState"), 3, "battle returns to the player's turn");
            combat.QueueFree();
            await Seconds(.1);

            // ---- Sister: swing, then defeat ----
            (combat, player, csm, enemy) = await SpawnBattle(isMale: false);
            sister = player.GetNode<CombatCharacterVisual>("Female-Character");
            brother = player.GetNode<CombatCharacterVisual>("Male-Character");
            Check(sister.Visible && !brother.Visible && player.ActiveVisual == sister, "sister selected from overworld choice");
            await Capture("combat-sister-idle");
            enemyHealth = enemy.health;
            csm.TransitionTo("PlayerAttackState");
            await Until(() => sister.CurrentState == "SwordSlash", 1, "sister enters SwordSlash");
            Check(sister.SwordSocket.Visible && brother.CurrentState == "Idle", "sister swings with sword; hidden brother stays idle");
            await Until(() => enemy.health < enemyHealth, 2, "sister's hit damages the enemy");
            await Capture("combat-sister-slash-hit");
            await Until(() => sister.CurrentState == "Idle" && !sister.SwordSocket.Visible, 2, "sister returns to Idle");

            player.health = 5;
            await Until(() => sister.CurrentState == "Defeated", 6, "lethal enemy hit plays the defeat");
            Check(player.health <= 0 && GodotObject.IsInstanceValid(player) && player.IsInsideTree(), "player model stays in the scene on defeat");
            await Seconds(2.5);
            Check(sister.CurrentState == "Defeated", "defeat pose holds instead of returning to Idle");
            Check(Mathf.Abs(Playback(sister).GetCurrentPlayPosition() - 5.0 / 24.0) < .01, "defeat holds TakeDamage frame 5, the deepest recoil");
            Check(IsState(csm, "DefeatedState"), "battle reaches DefeatedState");
            await Capture("combat-sister-defeated");
            combat.QueueFree();

            GD.Print("COMBAT_VALIDATION_PASS " + passed.Count + " checks");
            using var report = FileAccess.Open("res://Tests/Combat/validation-results.txt", FileAccess.ModeFlags.Write);
            report.StoreString(string.Join("\n", passed));
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PrintErr("COMBAT_VALIDATION_FAIL " + error.Message);
            GetTree().Quit(1);
        }
    }

    private async Task<(CombatMain, CombatPlayer, CombatStateMachine, CombatEnemy)> SpawnBattle(bool isMale)
    {
        var combat = GD.Load<PackedScene>("res://Scenes/CombatSystem/combat_main.tscn").Instantiate<CombatMain>();
        AddChild(combat);
        combat.ApplyOverworldCharacter(isMale);
        await Seconds(.2);
        return (combat, combat.GetNode<CombatPlayer>("%CombatPlayer"), combat.GetNode<CombatStateMachine>("CombatStateMachine"),
            combat.GetNode<CombatEnemy>("%CombatEnemy"));
    }

    private static AnimationNodeStateMachinePlayback Playback(CombatCharacterVisual actor) =>
        (AnimationNodeStateMachinePlayback)actor.AnimationTree.Get("parameters/playback");

    private static bool IsState(CombatStateMachine csm, string name) =>
        csm.CurrentState?.Name == name;

    private async Task Until(Func<bool> condition, double timeout, string message)
    {
        double end = Time.GetTicksMsec() / 1000.0 + timeout;
        while (!condition())
        {
            if (Time.GetTicksMsec() / 1000.0 > end) throw new Exception("timed out: " + message);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        }
        Check(true, message);
    }

    private async Task Seconds(double seconds) => await ToSignal(GetTree().CreateTimer(seconds), SceneTreeTimer.SignalName.Timeout);

    private async Task Capture(string label)
    {
        if (!capture) return;
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        GetViewport().GetTexture().GetImage().SavePng("res://Tests/Combat/" + label + ".png");
    }

    private void Check(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
        passed.Add("PASS " + message);
        GD.Print(passed[^1]);
    }
}
