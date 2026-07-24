using Godot;
using System;

public partial class CombatState : Node
{
	// Notifies the StateMachine to switch to another state
	[Signal]
	public delegate void TransitionedEventHandler(CombatStateMachine state, string newStateName);

	public CombatStateMachine csm;

	public virtual void Enter(){}

	public virtual void Exit(){}

	public virtual void Update(double delta){}
	
	public virtual void Ready(){}

	public virtual void HandleInput(InputEvent @event){}
}
