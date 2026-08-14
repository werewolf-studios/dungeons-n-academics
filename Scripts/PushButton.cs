using Godot;
using System;

public partial class PushButton : InteractionTest, MathSignal
{
    private String setValue;

    public string GetValue() { GD.Print("Sending");  return setValue; }

    //Functionality when something touches the button
    public void OnBodyEntered(string pushBlockValue)
    {
        GD.Print("Pressed: " + pushBlockValue);
        setValue = pushBlockValue;

        if (GetParent() is MathSystem) { GetParent<MathSystem>().ChangeDetected(); }
    }

    public void BodyEntered(Node3D body)
    {
        GD.Print("Pressed");
        
    }
}
