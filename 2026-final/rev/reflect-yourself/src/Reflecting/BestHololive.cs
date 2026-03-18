namespace ReflectYourself.Reflecting;

public class BestHololive
{
    public BestHololive(byte[] key)
    {
        Final = new TheFinal(key);
    }
    
    public string WelcomeTo => "Best hololive songs";

    public string FirstPlace => "https://www.youtube.com/watch?v=G3J06ircgMA";
    public string SecondPlace => "https://www.youtube.com/watch?v=a51VH9BYzZA";
    public string ThirdPlace => "https://www.youtube.com/watch?v=1A-UuoGQaOM";

    public string BonusMention => "ssm{placeholder} you won't be able to `strings | grep` this";

    public TheFinal Final { get; }
}