using System.Security.Cryptography;
using System.Text;

namespace ReflectYourself.Reflecting;

public class TheFinal
{
    private readonly byte[] _key;

    public TheFinal(byte[] key)
    {
        _key = key;
    }

    public string DecryptFlag()
    {
        using var aes = Aes.Create();
        aes.Key = _key;

        byte[] flag =
        [
            0x75, 0x21, 0xB6, 0x98, 0x9E, 0x00, 0xB7, 0x0F, 0x17, 0x89, 0xAE, 0x0A, 0x6F, 0x0C, 0x0E,
            0x94, 0x11, 0x44, 0x75, 0x78, 0xFE, 0x8E, 0xF0, 0xAF, 0x73, 0xA9, 0xDF, 0xC6, 0x42, 0xC6,
            0x55, 0xD3, 0xCD, 0x2B, 0xBE, 0x37, 0x3B, 0x64, 0x85, 0x9D, 0xE0, 0xDD, 0xBB, 0x96, 0xA1,
            0xDE, 0xA9, 0xAD
        ];

        var result = aes.DecryptEcb(flag, PaddingMode.PKCS7); // Add decryption

        try
        {
            return Encoding.UTF8.GetString(result);
        }
        catch (Exception e)
        {
            return "Couldn't decode flag";
        }
    }
}