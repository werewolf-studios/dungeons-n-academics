using Godot;
using System.Collections.Generic;

/// <summary>
/// Autoload that owns the player's graphics and audio settings: loads them from
/// user://settings.cfg at startup, applies them, and saves on every change.
/// </summary>
public partial class GameSettings : Node
{
	public static GameSettings Instance { get; private set; }

	public enum DisplayModeOption { Windowed, Borderless, Fullscreen }

	/// <summary>Where settings are stored. Tests point this at a separate file.</summary>
	public string ConfigPath { get; set; } = "user://settings.cfg";

	public DisplayModeOption DisplayMode { get; private set; } = DisplayModeOption.Windowed;
	public Vector2I Resolution { get; private set; } = new(1280, 720);
	public bool VSync { get; private set; } = true;
	public float RenderScale { get; private set; } = 1.0f;
	public float MasterVolume { get; private set; } = 1.0f;
	public float MusicVolume { get; private set; } = 0.8f;
	public float SfxVolume { get; private set; } = 0.8f;

	private static readonly Vector2I[] CommonResolutions =
	{
		new(1280, 720), new(1366, 768), new(1600, 900), new(1920, 1080), new(2560, 1440), new(3840, 2160),
	};

	public override void _Ready()
	{
		Instance = this;
		ProcessMode = ProcessModeEnum.Always;
		Load();
		ApplyAll();
	}

	/// <summary>Resolutions that fit on the current screen (always includes 1280x720).</summary>
	public List<Vector2I> AvailableResolutions()
	{
		Vector2I screen = HasWindow() ? DisplayServer.ScreenGetSize() : new Vector2I(3840, 2160);
		var list = new List<Vector2I>();
		foreach (var r in CommonResolutions)
			if (r.X <= screen.X && r.Y <= screen.Y) list.Add(r);
		if (!list.Contains(Resolution)) list.Add(Resolution);
		return list;
	}

	public void SetDisplayMode(DisplayModeOption mode) { DisplayMode = mode; ApplyDisplay(); Save(); }
	public void SetResolution(Vector2I size) { Resolution = size; ApplyDisplay(); Save(); }
	public void SetVSync(bool on) { VSync = on; ApplyVSync(); Save(); }
	public void SetRenderScale(float scale) { RenderScale = Mathf.Clamp(scale, 0.5f, 1f); ApplyRenderScale(); Save(); }
	public void SetMasterVolume(float v) { MasterVolume = Mathf.Clamp(v, 0f, 1f); ApplyBus("Master", MasterVolume); Save(); }
	public void SetMusicVolume(float v) { MusicVolume = Mathf.Clamp(v, 0f, 1f); ApplyBus("Music", MusicVolume); Save(); }
	public void SetSfxVolume(float v) { SfxVolume = Mathf.Clamp(v, 0f, 1f); ApplyBus("SFX", SfxVolume); Save(); }

	public void Load()
	{
		var cfg = new ConfigFile();
		if (cfg.Load(ConfigPath) != Error.Ok) return; // first run: keep defaults
		DisplayMode = (DisplayModeOption)(int)cfg.GetValue("graphics", "display_mode", (int)DisplayMode);
		Resolution = (Vector2I)cfg.GetValue("graphics", "resolution", Resolution);
		VSync = (bool)cfg.GetValue("graphics", "vsync", VSync);
		RenderScale = (float)cfg.GetValue("graphics", "render_scale", RenderScale);
		MasterVolume = (float)cfg.GetValue("audio", "master", MasterVolume);
		MusicVolume = (float)cfg.GetValue("audio", "music", MusicVolume);
		SfxVolume = (float)cfg.GetValue("audio", "sfx", SfxVolume);
	}

	public void Save()
	{
		var cfg = new ConfigFile();
		cfg.SetValue("graphics", "display_mode", (int)DisplayMode);
		cfg.SetValue("graphics", "resolution", Resolution);
		cfg.SetValue("graphics", "vsync", VSync);
		cfg.SetValue("graphics", "render_scale", RenderScale);
		cfg.SetValue("audio", "master", MasterVolume);
		cfg.SetValue("audio", "music", MusicVolume);
		cfg.SetValue("audio", "sfx", SfxVolume);
		cfg.Save(ConfigPath);
	}

	public void ApplyAll()
	{
		ApplyDisplay();
		ApplyVSync();
		ApplyRenderScale();
		ApplyBus("Master", MasterVolume);
		ApplyBus("Music", MusicVolume);
		ApplyBus("SFX", SfxVolume);
	}

	private static bool HasWindow() => DisplayServer.GetName() != "headless";

	private void ApplyDisplay()
	{
		if (!HasWindow()) return;
		switch (DisplayMode)
		{
			case DisplayModeOption.Fullscreen:
				DisplayServer.WindowSetMode(DisplayServer.WindowMode.ExclusiveFullscreen);
				break;
			case DisplayModeOption.Borderless:
				// Godot's "Fullscreen" mode is a borderless window covering the screen.
				DisplayServer.WindowSetMode(DisplayServer.WindowMode.Fullscreen);
				break;
			default:
				DisplayServer.WindowSetMode(DisplayServer.WindowMode.Windowed);
				DisplayServer.WindowSetFlag(DisplayServer.WindowFlags.Borderless, false);
				DisplayServer.WindowSetSize(Resolution);
				Vector2I screen = DisplayServer.ScreenGetSize();
				DisplayServer.WindowSetPosition(DisplayServer.ScreenGetPosition() + (screen - Resolution) / 2);
				break;
		}
	}

	private void ApplyVSync()
	{
		if (!HasWindow()) return;
		DisplayServer.WindowSetVsyncMode(VSync ? DisplayServer.VSyncMode.Enabled : DisplayServer.VSyncMode.Disabled);
	}

	private void ApplyRenderScale() => GetTree().Root.Scaling3DScale = RenderScale;

	private static void ApplyBus(string bus, float linear)
	{
		int index = AudioServer.GetBusIndex(bus);
		if (index < 0) return;
		AudioServer.SetBusMute(index, linear <= 0.001f);
		AudioServer.SetBusVolumeDb(index, Mathf.LinearToDb(Mathf.Max(linear, 0.0001f)));
	}
}
