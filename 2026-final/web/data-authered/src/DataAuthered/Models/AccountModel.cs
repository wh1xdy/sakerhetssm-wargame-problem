using System.ComponentModel.DataAnnotations;

namespace DataAuthered.Models;

public class AccountModel
{
    [Required(ErrorMessage = "Username is required")]
    public required string Username { get; set; }
}
