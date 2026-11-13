using Godot;

/// <summary>
/// Presentation only. Combat states ask for an attack, a flinch or a defeat; the
/// AnimationTree state machine (combat_state_machine.tres) picks the clip through
/// its advance conditions and returns to Idle on its own.
/// </summary>
public partial class CombatCharacterVisual : Node3D
{
    /// <summary>Emitted on the SwordSlash contact frame from the animation manifest.</summary>
    [Signal] public delegate void AttackHitEventHandler();

    [Export] public string CharacterId { get; set; } = "brother";

    public AnimationTree AnimationTree { get; private set; }
    public Node3D SwordSocket { get; private set; }
    public Node3D SpearSocket { get; private set; }
    public string CurrentState => playback?.GetCurrentNode().ToString() ?? "";

    private AnimationNodeStateMachinePlayback playback;
    private float swordHitTime;
    private bool hitSent;
    private string pendingCondition;
    private string pendingState;

    public override void _Ready()
    {
        AnimationTree = CharacterRig.FindChildOfType<AnimationTree>(this);
        var skeleton = CharacterRig.FindChildOfType<Skeleton3D>(this);
        using var manifest = CharacterRig.LoadManifest();
        var attachment = CharacterRig.AttachWeapons(skeleton, manifest.RootElement, CharacterId);
        SwordSocket = attachment.GetNode<Node3D>("SwordSocket");
        SpearSocket = attachment.GetNode<Node3D>("SpearSocket");
        swordHitTime = CharacterRig.EventTime(manifest.RootElement, "SwordSlash");

        playback = (AnimationNodeStateMachinePlayback)AnimationTree.Get("parameters/playback");
        AnimationTree.Active = true;
        // Run after the AnimationTree each frame so sword visibility and the hit
        // signal follow the state it just advanced to, not the previous frame's.
        ProcessPriority = AnimationTree.ProcessPriority + 1;
    }

    public void PlayAttack() => Request("attack", "SwordSlash");
    public void PlayHurt() => Request("hurt", "TakeDamage");
    public void PlayDefeated() => Request("defeated", "Defeated");

    public override void _Process(double delta)
    {
        string current = CurrentState;
        // A condition stays true until cleared, so clear it once its state is reached;
        // otherwise the automatic return to Idle would loop straight back in.
        if (pendingState != null && current == pendingState) ClearPending();

        bool slashing = current == "SwordSlash";
        SwordSocket.Visible = slashing || pendingState == "SwordSlash";
        if (!slashing)
        {
            hitSent = false;
        }
        else if (!hitSent && playback.GetCurrentPlayPosition() >= swordHitTime)
        {
            hitSent = true;
            EmitSignal(SignalName.AttackHit);
        }
    }

    private void Request(string condition, string state)
    {
        ClearPending();
        pendingCondition = condition;
        pendingState = state;
        AnimationTree.Set("parameters/conditions/" + condition, true);
    }

    private void ClearPending()
    {
        if (pendingCondition != null) AnimationTree.Set("parameters/conditions/" + pendingCondition, false);
        pendingCondition = null;
        pendingState = null;
    }
}
