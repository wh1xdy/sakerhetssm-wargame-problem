using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.DataProtection;

namespace DataAuthered;

public static class Program
{
    public static void Main(string[] args)
    {
        WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

        builder.Services.AddDataProtection();

        builder.Services
            .AddAuthentication()
            .AddCookie(CookieAuthenticationDefaults.AuthenticationScheme,
                o =>
                {
                    o.LoginPath = "/signin";
                    o.LogoutPath = "/signout";
                });

        builder.Services.AddAuthorization(o =>
        {
            o.AddPolicy("RequireAdmin", b => b.RequireRole("Admin"));
        });

        builder.Services.AddControllersWithViews();

        WebApplication app = builder.Build();

        app.UseAuthentication();
        app.UseAuthorization();

        app.UseStaticFiles();

        app.MapControllers();
        app.Run();
    }
}
