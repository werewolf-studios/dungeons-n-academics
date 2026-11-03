using Godot;
using System.Threading.Tasks;

/// <summary>Capture the real exploration camera; does not edit the source map.</summary>
public partial class ExplorationWorldReview : Node
{
    public override async void _Ready()
    {
        var world = GD.Load<PackedScene>("res://Scenes/player_controller_test.tscn").Instantiate();
        AddChild(world);
        // Keep review captures confined to exploration.
        foreach (string name in new[] { "EnemyX", "EnemyX2" })
            world.GetNode(name).ProcessMode = ProcessModeEnum.Disabled;
        await Frames(10);
        await Capture("brother-idle");
        Input.ActionPress("(Overworld) Walk");
        Input.ActionPress("(Overworld) Move Down");
        await Frames(18);
        await Capture("brother-walk");
        Input.ActionRelease("(Overworld) Walk");
        await Frames(16);
        await Capture("brother-run");
        Input.ActionRelease("(Overworld) Move Down");
        Input.ActionPress("(Temporary) Swap Character");
        await Frames(2);
        Input.ActionRelease("(Temporary) Swap Character");
        await Frames(10);
        await Capture("sister-idle");
        GD.Print("EXPLORATION_WORLD_REVIEW_PASS");
        GetTree().Quit();
    }

    private async Task Frames(int count)
    {
        for (int i = 0; i < count; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
    }

    private async Task Capture(string label)
    {
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        GetViewport().GetTexture().GetImage().SavePng("res://Tests/Exploration/" + label + ".png");
    }
}
