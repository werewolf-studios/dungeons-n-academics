using Godot;
using System;

public partial class CombatPlayer : Node3D
{
	/// <summary>Emitted when the active sibling's sword swing connects.</summary>
	[Signal]
	public delegate void AttackHitEventHandler();

	public int health = 30;
	private int damage = 10;

	private CombatCharacterVisual male;
	private CombatCharacterVisual female;

	public int Damage
	{
		get { return damage; }
		private set { damage = value; }
	}

	/// <summary>The sibling currently shown in battle.</summary>
	public CombatCharacterVisual ActiveVisual => female != null && female.Visible ? female : male;

	public override void _Ready()
	{
		male = GetNodeOrNull<CombatCharacterVisual>("Male-Character");
		female = GetNodeOrNull<CombatCharacterVisual>("Female-Character");
		foreach (var visual in new[] { male, female })
		{
			if (visual != null)
			{
				visual.AttackHit += () => EmitSignal(SignalName.AttackHit);
			}
		}
	}

	public void SetCharacterMale(bool isMale)
	{
		Node3D male = GetNodeOrNull<Node3D>("Male-Character");
		Node3D female = GetNodeOrNull<Node3D>("Female-Character");
		if (male != null)
		{
			male.Visible = isMale;
		}
		if (female != null)
		{
			female.Visible = !isMale;
		}
	}

	public void PlayAttack()
	{
		if (ActiveVisual == null)
		{
			// No animated model: still let the attack land.
			CallDeferred(GodotObject.MethodName.EmitSignal, SignalName.AttackHit);
			return;
		}
		ActiveVisual.PlayAttack();
	}

	public void PlayHurt()
	{
		ActiveVisual?.PlayHurt();
	}

	public void PlayDefeated()
	{
		ActiveVisual?.PlayDefeated();
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}

	public void TakeDamage(int damage)
	{
		health -= damage;
	}

	public void RemoveSelf()
	{
		QueueFree();
	}
}
