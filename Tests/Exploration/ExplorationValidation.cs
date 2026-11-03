using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

/// <summary>End-to-end checks against the real Player, InteractionTest and PushBlock.</summary>
public partial class ExplorationValidation : Node3D
{
    private readonly List<string> passed = new();
    private Player player;
    private ExplorationCharacterVisual male;
    private ExplorationCharacterVisual female;
    private const string Move = "(Overworld) Move Down"; // Existing controls: -Z.
    private const string Walk = "(Overworld) Walk";
    private const string Swap = "(Temporary) Swap Character";

    public override async void _Ready()
    {
        try
        {
            var floor = new StaticBody3D { Position = new Vector3(0, -0.5f, 0) };
            floor.AddChild(new CollisionShape3D { Shape = new BoxShape3D { Size = new Vector3(100, 1, 100) } });
            AddChild(floor);
            player = GD.Load<PackedScene>("res://Scenes/player.tscn").Instantiate<Player>();
            player.Speed = 10;
            AddChild(player);
            male = player.GetNode<ExplorationCharacterVisual>("Pivot/Male-Character");
            female = player.GetNode<ExplorationCharacterVisual>("Pivot/Female-Character");
            await Frames(5);
            Check(player.IsCharacterMale && male.Visible && !female.Visible, "brother selected at startup; both Pivot paths resolve");
            Check(male.CurrentClip == "Idle" && female.CurrentClip == "Idle", "both characters idle on spawn");
            Check(player.IsOnFloor() && Mathf.Abs(player.Position.Y) < .02f, "feet-at-origin visuals align with the unchanged grounded capsule");
            Check(InputMap.ActionGetEvents(Walk).Count == 2, "walk action includes keyboard and gamepad bindings");
            foreach (var actor in new[] { male, female })
            {
                Check(actor.AnimationPlayer.HasAnimation("SwordSlash") && actor.AnimationPlayer.HasAnimation("TakeDamage"), actor.CharacterId + " approved combat clips retained");
                var attachment = actor.FindChild("WeaponAttachment", true, false);
                var sword = attachment.GetNode<Node3D>("SwordSocket");
                var spear = attachment.GetNode<Node3D>("SpearSocket");
                Check(sword.Position.IsEqualApprox(new Vector3(.025f, .085f, 0)) && Mathf.IsEqualApprox(sword.RotationDegrees.X, -90), actor.CharacterId + " v10 sword socket");
                var seat = actor == male ? new Vector3(.08f, .07f, 0) : new Vector3(.07f, .065f, 0);
                Check(spear.Position.IsEqualApprox(seat) && Mathf.IsEqualApprox(spear.RotationDegrees.X, -90) && !spear.Visible && !sword.Visible, actor.CharacterId + " v10 spear socket; weapons hidden for locomotion");
            }
            Input.ActionPress(Move);
            await Frames(8);
            Check(Mathf.IsEqualApprox(player.GetRealVelocity().Length(), 10), "existing full movement speed preserved");
            Check(male.CurrentClip == "Run" && female.CurrentClip == "Run", "run follows movement for both siblings");
            Check(Mathf.IsEqualApprox(male.AnimationPlayer.SpeedScale, 1) && Mathf.IsEqualApprox(female.AnimationPlayer.SpeedScale, 1),
                "both siblings run at approved 1x timing at existing traversal speed");
            Check((-player.GetNode<Node3D>("Pivot").Basis.Z).Dot(Vector3.Forward) > .99f, "Pivot faces movement direction");
            Input.ActionPress(Walk);
            await Frames(8);
            Check(male.CurrentClip == "Walk" && player.GetRealVelocity().Length() < 4, "walk modifier reduces speed and selects Walk");
            Check(Mathf.IsEqualApprox(male.AnimationPlayer.SpeedScale, 1) && Mathf.IsEqualApprox(female.AnimationPlayer.SpeedScale, 1),
                "both siblings walk at approved 1x timing");
            Input.ActionPress(Swap);
            await Frames(5);
            Check(!player.IsCharacterMale && !male.Visible && female.Visible && female.CurrentClip == "Walk", "moving swap selects sister without losing locomotion");
            await Frames(5);
            Check(!player.IsCharacterMale, "holding swap does not toggle repeatedly");
            Input.ActionRelease(Swap);
            Input.ActionRelease(Walk);
            Input.ActionRelease(Move);
            await Frames(5);
            Check(female.CurrentClip == "Idle", "release returns to Idle");
            Check(female.GlobalBasis.Z.Dot(-player.GetNode<Node3D>("Pivot").GlobalBasis.Z) > .99f,
                "sister model +Z faces the controller's -Z forward");
            Input.ActionPress(Swap);
            await Frames(2);
            Input.ActionRelease(Swap);
            Check(player.IsCharacterMale && male.Visible && !female.Visible, "idle swap returns to brother");
            Check(male.GetNode<Node3D>("Model").GlobalBasis.Z.Dot(-player.GetNode<Node3D>("Pivot").GlobalBasis.Z) > .99f,
                "brother model +Z faces the controller's -Z forward");
            Input.ActionPress(Move);
            Input.ActionPress("(Overworld) Move Right");
            await Frames(5);
            Check(Mathf.IsEqualApprox(new Vector2(player.GetRealVelocity().X, player.GetRealVelocity().Z).Length(), player.Speed),
                "diagonal movement remains normalized");
            Input.ActionRelease("(Overworld) Move Right");
            Input.ActionRelease(Move);
            await Frames(3);
            player.ProcessMode = ProcessModeEnum.Disabled;
            double animationTime = male.AnimationPlayer.CurrentAnimationPosition;
            Vector3 pausedPosition = player.Position;
            Input.ActionPress(Move);
            await Frames(5);
            Check(player.Position.IsEqualApprox(pausedPosition) && Mathf.IsEqualApprox(male.AnimationPlayer.CurrentAnimationPosition, animationTime),
                "existing scene-manager disable freezes movement and animation together");
            Input.ActionRelease(Move);
            player.ProcessMode = ProcessModeEnum.Inherit;
            await Frames(3);

            player.Position = Vector3.Zero;
            var wall = new StaticBody3D { Position = new Vector3(0, 1, -2) };
            wall.AddChild(new CollisionShape3D { Shape = new BoxShape3D { Size = new Vector3(10, 4, 1) } });
            AddChild(wall);
            Input.ActionPress(Move);
            await Frames(30);
            Check(player.Position.Z > -1.1f && male.CurrentClip == "Idle", "wall collision blocks travel and stops Run");
            Input.ActionRelease(Move);
            wall.QueueFree();
            await Frames(3);
            foreach (bool sister in new[] { false, true })
            {
                if (sister) { Input.ActionPress(Swap); await Frames(2); Input.ActionRelease(Swap); }
                player.Position = Vector3.Zero;
                await Frames(3);
                var interact = GD.Load<PackedScene>("res://Scenes/interaction_test.tscn").Instantiate<InteractionTest>();
                interact.Position = new Vector3(0, 1, -1.1f);
                AddChild(interact);
                await Frames(5);
                var mesh = interact.GetNode<MeshInstance3D>("MeshInstance3D");
                var before = mesh.MaterialOverride;
                Input.ActionPress("AttackInteract");
                await Frames(4);
                Check(mesh.MaterialOverride != before, (sister ? "sister" : "brother") + " forward interaction still works");
                var after = mesh.MaterialOverride;
                await Frames(4);
                Check(mesh.MaterialOverride == after, "holding interact triggers once");
                Input.ActionRelease("AttackInteract");
                interact.QueueFree();
                await Frames(3);
                var grid = new GridMap();
                AddChild(grid);
                var block = GD.Load<PackedScene>("res://Scenes/push_block.tscn").Instantiate<PushBlock>();
                block.Position = new Vector3(1, 1, 1);
                grid.AddChild(block);
                block.SetValue(0);
                block.Initialize(grid);
                player.Position = new Vector3(1, 0, 3);
                await Frames(3);
                Vector3 initial = block.Position;
                Input.ActionPress(Walk);
                Input.ActionPress(Move);
                await Frames(35);
                Input.ActionRelease(Move);
                Input.ActionRelease(Walk);
                Check(block.Position.Z < initial.Z - 1, (sister ? "sister" : "brother") + " walking into a block still pushes on the grid");
                grid.QueueFree();
                await Frames(3);
            }
            GD.Print("EXPLORATION_VALIDATION_PASS " + passed.Count + " checks");
            using var report = FileAccess.Open("res://Tests/Exploration/validation-results.txt", FileAccess.ModeFlags.Write);
            report.StoreString(string.Join("\n", passed));
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PrintErr("EXPLORATION_VALIDATION_FAIL " + error);
            GetTree().Quit(1);
        }
    }

    private async Task Frames(int count)
    {
        for (int i = 0; i < count; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
    }

    private void Check(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
        passed.Add("PASS " + message);
        GD.Print(passed[^1]);
    }
}
