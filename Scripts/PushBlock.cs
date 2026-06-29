using Godot;
using System.Threading.Tasks;

[GlobalClass]
public partial class PushBlock : CharacterBody3D
{
    GridMap grid;
    bool isMoving = false;
    Tween tween;

    [Export]
    float slidingTime = 0.3f;

    /// <summary>
    /// Initializes the grid and puts our push block at a default location
    /// </summary>
    /// <param name="_grid"></param>
    public void Initialize(GridMap _grid)
    {
        grid = _grid; 
        Position = CalculateDestination(Vector3.Zero);
    }

    /// <summary>
    /// Checks if the box isn't moving and moves it based on the players collision
    /// </summary>
    /// <param name="velocity"></param>
    /// <returns></returns>
    public async Task Push(Vector3 velocity)
    {
        if(isMoving)
        {
            return;
        }
        Vector3 moveTo = CalculateDestination(velocity.Normalized());
        if(CanMove(moveTo))
        {
            tween = GetTree().CreateTween();
            isMoving = true;
            tween.TweenProperty(this, "GlobalPosition", moveTo, slidingTime).SetEase(Tween.EaseType.Out).SetTrans(Tween.TransitionType.Cubic);
            await ToSignal(tween, Tween.SignalName.Finished);
            isMoving = false;

        }
    }
    
    /// <summary>
    /// Keeps the push block in the grid by moving it one unit at a time on our GridMap
    /// </summary>
    /// <param name="dir"></param>
    /// <returns></returns>
    public Vector3 CalculateDestination(Vector3 dir)
    {
        Vector3I gridMapPos = grid.LocalToMap(GlobalPosition) + (Vector3I)dir.Round();
        return grid.MapToLocal(gridMapPos);
    }

    /// <summary>
    /// Method used to check if the box is moving or not
    /// </summary>
    /// <param name="moveTo"></param>
    /// <returns></returns>
    public bool CanMove(Vector3 moveTo)
    {
        Transform3D futureTransform = Transform;
        futureTransform.Origin = moveTo;
        return !TestMove(futureTransform, Vector3.Zero);
    }

}
