using Godot;
using System.Text.Json;

/// <summary>
/// Reads reusable puzzle equation banks. The shared JSON groups equations by
/// category so other puzzles can roll from the same file later.
/// </summary>
public static class PuzzleEquationBank
{
    public const string DefaultPath = "res://QuestionsFolder/Puzzles/puzzle_equations.json";

    public sealed class Entry
    {
        public string Text { get; init; } = "";
        public int Answer { get; init; }
    }

    /// <summary>Picks a random equation entry from <paramref name="category"/>.</summary>
    public static Entry Roll(string path, string category)
    {
        if (!FileAccess.FileExists(path))
        {
            GD.PushError($"PuzzleEquationBank: missing {path}");
            return null;
        }

        using var document = JsonDocument.Parse(FileAccess.GetFileAsString(path));
        if (!document.RootElement.TryGetProperty(category, out JsonElement list) ||
            list.ValueKind != JsonValueKind.Array)
        {
            GD.PushError($"PuzzleEquationBank: category '{category}' not found in {path}");
            return null;
        }

        int count = list.GetArrayLength();
        if (count == 0)
        {
            GD.PushError($"PuzzleEquationBank: category '{category}' is empty");
            return null;
        }

        JsonElement entry = list[GD.RandRange(0, count - 1)];
        return new Entry
        {
            Text = entry.GetProperty("text").GetString() ?? "? + ? = ?",
            Answer = entry.GetProperty("answer").GetInt32(),
        };
    }
}
