using Godot;
using System;
using System.Linq;
using System.Collections.Generic;

public partial class EnemyManager : Node
{
	private List<CombatEnemy> enemies = new List<CombatEnemy>();

	[Export]
	public CombatPlayer player { get; set; }

	public override void _Ready()
	{
		enemies = GetChildren().OfType<CombatEnemy>().ToList();
	}

	public override void _Process(double delta)
	{
		// Remove any null nodes from the enemies list.
		enemies.RemoveAll(node => !GodotObject.IsInstanceValid(node));
	}

	/// <summary>True while at least one enemy still has hit points.</summary>
	public bool AnyEnemyAlive()
	{
		foreach (var enemy in enemies)
		{
			if (GodotObject.IsInstanceValid(enemy) && enemy.health > 0)
			{
				return true;
			}
		}
		return false;
	}

	/// <summary>
	/// A dead enemy stays in the list while its death animation plays, so victory
	/// must be decided by health, not by node count.
	/// </summary>
	public bool AllEnemiesDead() => !AnyEnemyAlive();

	public bool IsEnemyDead(int index)
	{
		return index < 0 || index >= enemies.Count
			|| !GodotObject.IsInstanceValid(enemies[index])
			|| enemies[index].health <= 0;
	}

	public void DamageEnemies() => DamageEnemies(player.Damage);

	/// <summary>Applies an explicit damage amount (used by the spear Special).</summary>
	public void DamageEnemies(int damage)
	{
		if (enemies.Count == 1 && !IsEnemyDead(0))
		{
			enemies[0].TakeDamage(damage);
		}
	}

	public void CheckIfEnemiesDead()
	{
		// CheckIfDead itself ignores live/already-dying enemies; this guard only
		// filters an invalid node, so a 0-HP enemy still plays its Death animation.
		if (enemies.Count == 1 && GodotObject.IsInstanceValid(enemies[0]))
		{
			enemies[0].CheckIfDead();
		}
	}

	public void DealDamage()
	{
		if (enemies.Count == 1 && !IsEnemyDead(0))
		{
			player.TakeDamage(enemies[0].Damage);
		}
	}

	// -------- Animation Managing --------

	public void PlayAttackAnim()
	{
		if (enemies.Count == 1 && !IsEnemyDead(0))
		{
			enemies[0].PlayAnim("Shoot");
		}
	}

	public void PlayIdleAnim()
	{
		if (enemies.Count == 1 && GodotObject.IsInstanceValid(enemies[0]))
		{
			enemies[0].PlayAnim("Idle_Float");
		}
	}

	/// <summary>Health for the HUD; 0 when the enemy is already gone.</summary>
	public int getEnemyHealth(int index)
	{
		if (index < 0 || index >= enemies.Count || !GodotObject.IsInstanceValid(enemies[index]))
		{
			return 0;
		}
		return Math.Max(0, enemies[index].health);
	}
}
