using DataAuthered.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuGet.Packaging;

namespace DataAuthered.Controllers;

[Controller]
[Route("/")]
public class MainController : Controller
{
    public IActionResult Index()
    {
        return View();
    }


    [HttpGet("flag")]
    [Authorize("RequireAdmin")]
    public IActionResult Flag()
    {
        return View(new FlagModel()
        {
            Flag = Environment.GetEnvironmentVariable("FLAG") ?? "ssm{placeholder}"
        });
    }

    [HttpGet("file")]
    [Authorize]
    public IActionResult ReadFileAsync([FromQuery] string path)
    {
        path = Path.GetFullPath(path);
        

        if (path.StartsWith("/proc"))
        {
            return BadRequest("No proc access");
        }


        if (!Path.Exists(path))
        {
            return NotFound();
        }

        FileAttributes attr = System.IO.File.GetAttributes(path);
        if (attr.HasFlag(FileAttributes.Directory))
        {
            string[] paths = Directory.GetDirectories(path).Concat(Directory.GetFiles(path))
                .ToArray();
            return Ok(string.Join('\n', paths));
        }

        Stream fileStream = System.IO.File.OpenRead(path);
        return File(fileStream, "application/octet-stream");
    }
}
