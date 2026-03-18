namespace ReflectYourself.Reflecting;

public static class TheMazeEntrance
{
    static TheMazeEntrance()
    {
        Members = new BestHololiveMember(
            [
                0x65, 0x62, 0xcd, 0x28, 0x9b, 0xd4, 0x41, 0x4d, 0x9a, 0x90, 0xd7, 0x22, 0x11, 0xb0, 0x44, 0x44,
                0x9d, 0x27, 0xc0, 0xed, 0xee, 0xac, 0xdd, 0x4a, 0xf3, 0xaa, 0x09, 0xb5, 0x3d, 0x6d, 0xd5, 0x9c
            ]
        );
    }

    private readonly static string _title = "You found the entrance of the maze :), good luck. This is a mess";

    public static string Description =>
        "I have hidden a bunch of stuff here. Good luck finding the flag! Oh also, nothting here is AI generated";

    public static TopGuraA TheTopA { get; } = new();
    public static BestHololiveMember Members { get; }
}