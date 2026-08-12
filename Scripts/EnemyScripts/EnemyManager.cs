using Godot;
using System.Linq;
using System.Collections.Generic;
using System.Net.Mail;

public partial class EnemyManager : Node
{
	private List<MeshInstance3D> enemies;

	[Export]
	public CombatPlayer player { get; set; }

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		enemies = GetChildren().OfType<MeshInstance3D>().ToList();

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
		enemies = GetChildren().OfType<MeshInstance3D>().ToList();

		if (enemies.Count == 1)
		{
			//Cast the MeshInstance into the CombatEnemy script it holds
			CombatEnemy ce = enemies[0] as CombatEnemy;
			ce.TakeDamage(player.Damage);
		}
	}

}
