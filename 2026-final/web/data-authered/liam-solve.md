1. fetch /file?path=/root/.aspnet/DataProtection-Keys
2. hitta nyckeln och printa innehållet
3. lokalt ändra så signup ger admin roll
4. ändra till .PersistKeysToFileSystem(new DirectoryInfo("/keys")); i Program.cs
5. i Dockerfile lägg in nyckeln från remote och lägg den i /keys
6. lokalt skapa en user
7. kopiera cookin och pastea in i remote och då blir man admin
