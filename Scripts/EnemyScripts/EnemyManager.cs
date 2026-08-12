using Godot;
using System.Linq;
using System.Collections.Generic;
using System.Net.Mail;

public partial class EnemyManager : Node
{
	private List<CombatEnemy> enemies = new List<CombatEnemy>();

	[Export]
	public CombatPlayer player { get; set; }

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		enemies = GetChildren().OfType<CombatEnemy>().ToList();

		//Attach animation signal(s?) to enemies
		foreach (MeshInstance3D enemy in enemies)
		{
			//Cast the MeshInstance into the CombatEnemy script it holds
			CombatEnemy ce = enemy as CombatEnemy;
		}
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}

	public void DealDamage()
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

	// -------- Animation Managing --------

	// WITH MULTIPLE ENEMIES, ANIMATION PLAYING WILL NEED TO BE
	// REWORKED AS EACH ENEMY TAKES ITS TURN ATTACKING
	public void PlayAttackAnim()
	{
		if (enemies.Count == 0)
		{
			enemies[0].PlayAnim("Shoot");
		}
	}
}
