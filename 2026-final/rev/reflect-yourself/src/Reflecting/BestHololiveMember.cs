namespace ReflectYourself.Reflecting;

public class BestHololiveMember
{
    public BestHololiveMember(byte[] key)
    {
        Songs = new BestHololive(key);
    }

    public string ElloGuysTodayIVillPResent => "Best hololive members";

    private readonly string numberoUno = "Nakiri Ayame";
    public string NumberoDos => "Tokoyami Towa";
    internal string NumberoTres => "Shirakami Fubuki";
    internal readonly string numberoCuatro = "Hoshimachi Suisei";
    private string NumberoCinco => "Gigi Murin";

    public string ThankU => "For watching, plz also watch";
    public BestHololive Songs { get; }
}