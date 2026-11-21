using Godot;
using System;

public partial class CombatPlayer : Node3D
{
	/// <summary>Emitted when the active sibling's sword swing connects.</summary>
	[Signal]
	public delegate void AttackHitEventHandler();

	/// <summary>Emitted when the active sibling's spear thrust connects.</summary>
	[Signal]
	public delegate void SpecialHitEventHandler();

	public const int MaxHealth = PlayerSaveData.MaxHealth;

	public int health = MaxHealth;
	private int damage = 10;

	private CombatCharacterVisual male;
	private CombatCharacterVisual female;

	/// <summary>
	/// Start from the persistent pool before any state reads health. _EnterTree runs
	/// before sibling nodes' _Ready, so PlayerTurnState sees the saved value.
	/// </summary>
	public override void _EnterTree()
	{
		var data = SaveManager.Instance?.PlayerData;
		if (data == null) return;
		health = data.Health;
		if (health <= 0)
		{
			// A previous defeat should never force the next battle to start dead.
			health = MaxHealth;
			data.Health = MaxHealth;
		}
	}

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
				visual.SpecialHit += () => EmitSignal(SignalName.SpecialHit);
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

	public void PlaySpecial()
	{
		if (ActiveVisual == null)
		{
			CallDeferred(GodotObject.MethodName.EmitSignal, SignalName.SpecialHit);
			return;
		}
		ActiveVisual.PlaySpecial();
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
		SyncToSave();
	}

	/// <summary>Restores hit points up to MaxHealth and returns the amount actually healed.</summary>
	public int Heal(int amount)
	{
		int before = health;
		health = Math.Min(MaxHealth, health + Math.Max(0, amount));
		SyncToSave();
		return health - before;
	}

	/// <summary>Mirrors combat damage/healing into the persistent exploration pool.</summary>
	private void SyncToSave()
	{
		var data = SaveManager.Instance?.PlayerData;
		if (data != null)
		{
			data.Health = health;
		}
	}

	public void RemoveSelf()
	{
		QueueFree();
	}
}
