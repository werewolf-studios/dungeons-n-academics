using Godot;
using System.Threading.Tasks;

[GlobalClass]
public partial class PushBlock : InteractionTest
{
    [Export]
    string value;

    GridMap grid;
    bool isMoving = false;
    Tween tween;

    [Export]
    float slidingTime = 0.3f;

    [Export]
    private bool interactRequired;

    public string GetValue()
    {
        return value;
    } 

    /// <summary>
    /// Initializes the grid 
    /// </summary>
    /// <param name="_grid"></param>    
    public void Initialize(GridMap _grid)
    {
        grid = _grid;
        Position = Vector3.Zero;
    }

    public override void Interaction(Player origin)
    {
        Push(origin.Velocity, true);
    }

    /// <summary>
    /// Checks if the box isn't moving and moves it based on the players collision
    /// </summary>
    /// <param name="velocity"></param>
    /// <returns></returns>
    public async Task Push(Vector3 velocity, bool interactSwitch)
    {
        GD.Print(velocity);
        if (isMoving || (interactRequired !& interactSwitch))
        {
            return;
        }

        Vector3 moveTo = CalculateDestination(velocity.Normalized());

        if (CanMove(moveTo))
        {
            //Start tween for smooth box movement 
            tween = GetTree().CreateTween();
            isMoving = true;
            tween.TweenProperty(this, "global_position", moveTo, slidingTime)
                .SetEase(Tween.EaseType.Out)
                .SetTrans(Tween.TransitionType.Cubic);
            await ToSignal(tween, Tween.SignalName.Finished);
            isMoving = false;
        }

        GD.Print(moveTo);
        GD.Print(GlobalPosition);


    }

    /// <summary>
    /// Keeps the push block in the grid by moving it one unit at a time on our GridMap
    /// </summary>
    /// <param name="dir"></param>
    /// <returns></returns>
    public Vector3 CalculateDestination(Vector3 dir)
    {
        Vector3 localPos = grid.ToLocal(GlobalPosition);
        Vector3I gridMapPos = grid.LocalToMap(localPos) + (Vector3I)dir.Round();
        Vector3 localDestination = grid.MapToLocal(gridMapPos);
        //Locks Y axis movement
        localDestination.Y = 0.0f;
        return grid.ToGlobal(localDestination);
    }

    /// <summary>
    /// Method used to check if the box is moving or not
    /// </summary>
    /// <param name="moveTo"></param>
    /// <returns></returns>
    public bool CanMove(Vector3 moveTo)
    {
        Transform3D currentTransform = GlobalTransform;
        Vector3 motion = moveTo - GlobalPosition;
        return !TestMove(currentTransform, motion);
    }

}
