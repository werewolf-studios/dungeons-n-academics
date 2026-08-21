using Godot;
using System;
using System.Collections.Generic;
using System.Data;
using System.Runtime.Serialization;

public partial class CombatStateMachine : Node
{
	[Export] public CombatState initialState;

	private Dictionary<string, CombatState> states;

	private CombatState currentState;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		GD.Print("1. CombatStateMachine _Ready started");

		states = new Dictionary<string, CombatState>();
		foreach (Node node in GetChildren())
		{
			if (node is CombatState s)
			{
				states[node.Name.ToString()] = s;
				s.csm = this;
				s.Initialize();
				s.Exit(); // reset all states
			}
		}

		if (initialState != null)
		{
    		currentState = initialState;
			currentState.Enter();
			GD.Print($"2. Current state successfully set to: {currentState.Name}");
		}
		else
		{
    		GD.PrintErr("3. Erorr: initialState is null in Inspector");
		}
		

	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		currentState.Update((float) delta);
	}

    public override void _UnhandledInput(InputEvent @event)
    {
        currentState.HandleInput(@event);
    }

	public void TransitionTo(string key)
	{
		if (currentState == null || !states.TryGetValue(key, out CombatState nextState) || currentState == nextState)
		{
			return;
		}

		currentState.Exit();
		currentState = nextState;
		currentState.Enter();
	}
}
