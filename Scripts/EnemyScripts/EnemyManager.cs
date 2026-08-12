using Godot;
using System.Linq;
using System.Collections.Generic;
using System.Net.Mail;
// READ THE COMMENT AT THE FUNCTIONS SECTION

public partial class EnemyManager : Node
{
	private List<CombatEnemy> enemies = new List<CombatEnemy>();

	[Export]
	public CombatPlayer player { get; set; }

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		enemies = GetChildren().OfType<CombatEnemy>().ToList();
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		// Remove any null nodes from the enemies list.
		enemies.RemoveAll(node => !GodotObject.IsInstanceValid(node));
	}

	// Code will need to be refactored for when a battle has multiple enemies.
	// The player will need to be able to select enemies and actions will be
	// dealt only to that enemy. Enemies will also have to attack separately
	// from each other. The code here was from a simple prototype to get the
	// absolute basics done.

	public void DamageEnemies()
	{
		if (enemies.Count == 1)
		{
			enemies[0].TakeDamage(player.Damage);
		}
	}

	public void CheckIfEnemiesDead()
	{
		if (enemies.Count == 1)
		{
			enemies[0].CheckIfDead();
		}
	}

	public bool AllEnemiesDead()
	{
		if (enemies.Count == 0)
		{
			return true;
		}
		else return false;
	}

	public void DealDamage()
	{
		if (enemies.Count == 1)
		{
			player.TakeDamage(enemies[0].Damage);
		}
	}

	// -------- Animation Managing --------

	// With multiple enemies, animation playing will need to be
	// reworked as each enemy takes its turn attacking. Animation
	// names will need to be renamed.
	public void PlayAttackAnim()
	{
		if (enemies.Count == 1)
		{
			enemies[0].PlayAnim("Shoot");
		}
	}

	public void PlayIdleAnim()
	{
		if (enemies.Count == 1)
		{
			enemies[0].PlayAnim("Idle_Float");
		}
	}
}
