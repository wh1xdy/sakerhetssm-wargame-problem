using System.Security.Claims;
using DataAuthered.Models;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DataAuthered.Controllers;

[Controller]
[Route("/signin")]
public class AccountController : Controller
{
    public IActionResult Index()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> SignInAsync(AccountModel model)
    {
        if (!ModelState.IsValid)
        {
            return View("Index", model);
        }

        ClaimsIdentity identity = new([new Claim(ClaimTypes.Name, model.Username)],
            CookieAuthenticationDefaults.AuthenticationScheme);
        await this.HttpContext.SignInAsync(new ClaimsPrincipal(identity),
            new AuthenticationProperties
            {
                IsPersistent = true,
                ExpiresUtc = DateTime.UtcNow.AddHours(1)
            });

        return Redirect("/");
    }

    [HttpGet("/signout")]
    public async Task<IActionResult> SignOutAsync(AccountModel model)
    {
        await this.HttpContext.SignOutAsync();
        return Redirect("/");
    }
}
