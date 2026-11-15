using Godot;
using System.Collections.Generic;

/// <summary>
/// Shared settings panel (Scenes/UI/settings_panel.tscn) used by the main menu and the
/// pause menu. Graphics and Audio tabs read and write GameSettings; the Controls tab
/// lists keyboard and gamepad controls. LB/RB (Q/E) switch tabs, B/Esc closes.
/// </summary>
public partial class SettingsPanel : Control
{
	[Signal] public delegate void ClosedEventHandler();

	private Button[] tabs;
	private Control[] pages;
	private int currentTab;

	private OptionButton displayMode;
	private OptionButton resolution;
	private CheckButton vsync;
	private HSlider renderScale;
	private HSlider master;
	private HSlider music;
	private HSlider sfx;
	private Button back;
	private List<Vector2I> resolutions = new();

	public override void _Ready()
	{
		var box = GetNode<Control>("Center/Panel/Margin/VBox");
		tabs = new[] { box.GetNode<Button>("Tabs/Graphics"), box.GetNode<Button>("Tabs/Audio"), box.GetNode<Button>("Tabs/Controls") };
		pages = new[] { box.GetNode<Control>("Pages/GraphicsPage"), box.GetNode<Control>("Pages/AudioPage"), box.GetNode<Control>("Pages/ControlsPage") };
		back = box.GetNode<Button>("Back");

		var g = pages[0];
		displayMode = g.GetNode<OptionButton>("DisplayModeRow/Row/DisplayMode");
		resolution = g.GetNode<OptionButton>("ResolutionRow/Row/Resolution");
		vsync = g.GetNode<CheckButton>("VSyncRow/Row/VSync");
		renderScale = g.GetNode<HSlider>("RenderScaleRow/Row/RenderScale");
		var a = pages[1];
		master = a.GetNode<HSlider>("MasterRow/Row/Master");
		music = a.GetNode<HSlider>("MusicRow/Row/Music");
		sfx = a.GetNode<HSlider>("SfxRow/Row/Sfx");

		for (int i = 0; i < tabs.Length; i++)
		{
			int index = i;
			tabs[i].FocusEntered += () => ShowTab(index);
			tabs[i].Pressed += () => ShowTab(index);
		}
		back.Pressed += Close;

		displayMode.AddItem("Windowed");
		displayMode.AddItem("Borderless Fullscreen");
		displayMode.AddItem("Fullscreen");
		displayMode.ItemSelected += i =>
		{
			GameSettings.Instance.SetDisplayMode((GameSettings.DisplayModeOption)(int)i);
			resolution.Disabled = i != (int)GameSettings.DisplayModeOption.Windowed;
		};
		resolution.ItemSelected += i => GameSettings.Instance.SetResolution(resolutions[(int)i]);
		vsync.Toggled += on => GameSettings.Instance.SetVSync(on);
		renderScale.ValueChanged += v => { GameSettings.Instance.SetRenderScale((float)v / 100f); UpdateValueLabel(renderScale); };
		master.ValueChanged += v => { GameSettings.Instance.SetMasterVolume((float)v / 100f); UpdateValueLabel(master); UiFeedback.Instance?.Tick(); };
		music.ValueChanged += v => { GameSettings.Instance.SetMusicVolume((float)v / 100f); UpdateValueLabel(music); };
		sfx.ValueChanged += v => { GameSettings.Instance.SetSfxVolume((float)v / 100f); UpdateValueLabel(sfx); UiFeedback.Instance?.Tick(); };

		// Highlight the whole row of whichever option has focus.
		foreach (Control control in new Control[] { displayMode, resolution, vsync, renderScale, master, music, sfx })
		{
			var row = control.GetParent().GetParent<PanelContainer>();
			control.FocusEntered += () => row.ThemeTypeVariation = "SettingsRowFocused";
			control.FocusExited += () => row.ThemeTypeVariation = "SettingsRow";
		}

		Visible = false;
	}

	public void Open()
	{
		SyncFromSettings();
		Visible = true;
		ShowTab(0);
		tabs[0].CallDeferred(Control.MethodName.GrabFocus);
	}

	public void Close()
	{
		if (!Visible) return;
		Visible = false;
		EmitSignal(SignalName.Closed);
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (!Visible) return;
		if (@event.IsActionPressed("ui_cancel"))
		{
			UiFeedback.Instance?.Back();
			Close();
			GetViewport().SetInputAsHandled();
		}
		else if (@event.IsActionPressed("Menu Tab Left") || @event.IsActionPressed("Menu Tab Right"))
		{
			int step = @event.IsActionPressed("Menu Tab Left") ? -1 : 1;
			int next = (currentTab + step + tabs.Length) % tabs.Length;
			UiFeedback.Instance?.Tick();
			ShowTab(next);
			tabs[next].GrabFocus();
			GetViewport().SetInputAsHandled();
		}
	}

	private void ShowTab(int index)
	{
		currentTab = index;
		for (int i = 0; i < tabs.Length; i++)
		{
			tabs[i].SetPressedNoSignal(i == index);
			pages[i].Visible = i == index;
		}

		// Gamepad routes: tabs -> first option -> ... -> last option -> Back -> tabs.
		var options = FocusableOptions(pages[index]);
		Control first = options.Count > 0 ? options[0] : back;
		Control last = options.Count > 0 ? options[^1] : null;
		foreach (var tab in tabs) tab.FocusNeighborBottom = tab.GetPathTo(first);
		if (options.Count > 0)
		{
			foreach (var option in options) option.FocusNeighborTop = option.FocusNeighborBottom = new NodePath();
			options[0].FocusNeighborTop = options[0].GetPathTo(tabs[index]);
			last.FocusNeighborBottom = last.GetPathTo(back);
			back.FocusNeighborTop = back.GetPathTo(last);
		}
		else
		{
			back.FocusNeighborTop = back.GetPathTo(tabs[index]);
		}
		back.FocusNeighborBottom = back.GetPathTo(tabs[index]);
	}

	private static List<Control> FocusableOptions(Control page)
	{
		var list = new List<Control>();
		foreach (Node row in page.GetChildren())
			if (row.GetNodeOrNull("Row") is Node inner)
				foreach (Node child in inner.GetChildren())
					if (child is Control c && c.FocusMode != FocusModeEnum.None) list.Add(c);
		return list;
	}

	private void SyncFromSettings()
	{
		var s = GameSettings.Instance;
		displayMode.Select((int)s.DisplayMode);
		resolutions = s.AvailableResolutions();
		resolution.Clear();
		foreach (var r in resolutions) resolution.AddItem($"{r.X} x {r.Y}");
		resolution.Select(resolutions.IndexOf(s.Resolution));
		resolution.Disabled = s.DisplayMode != GameSettings.DisplayModeOption.Windowed;
		vsync.SetPressedNoSignal(s.VSync);
		renderScale.SetValueNoSignal(Mathf.Round(s.RenderScale * 100));
		master.SetValueNoSignal(Mathf.Round(s.MasterVolume * 100));
		music.SetValueNoSignal(Mathf.Round(s.MusicVolume * 100));
		sfx.SetValueNoSignal(Mathf.Round(s.SfxVolume * 100));
		foreach (var slider in new[] { renderScale, master, music, sfx }) UpdateValueLabel(slider);
	}

	private static void UpdateValueLabel(HSlider slider) =>
		slider.GetParent().GetNode<Label>("Value").Text = $"{slider.Value:0}%";
}
