using Godot;
using System;

public partial class PushButton : InteractionTest, MathSignal
{
    private PushBlock currentBlock;

    //Functionality when something touches the button
    public void OnBodyEntered(Object pushBlock)
    {
        GD.Print("Pressed");
        if (pushBlock is PushBlock newBlock) { currentBlock = newBlock; }
    }

    public string GetValue() {  return currentBlock.GetValue(); }
}
