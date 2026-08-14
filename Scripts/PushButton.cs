using Godot;
using System;

public partial class PushButton : InteractionTest, MathSignal
{
    private String setValue;

    public string GetValue() { return setValue; }

    //Functionality when something touches the button
    public void OnBodyEntered(string pushBlockValue)
    {
        GD.Print("Pressed");
        setValue = pushBlockValue;

        if (GetParent() is MathSystem) { GetParent<MathSystem>().ChangeDetected(); }
    }
}
