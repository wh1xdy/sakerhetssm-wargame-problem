FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY ./ /src
RUN dotnet restore
COPY . .
RUN dotnet build -c Release
RUN dotnet tool install -g Microsoft.Web.LibraryManager.Cli

WORKDIR "/src"
RUN $HOME/.dotnet/tools/libman restore
RUN dotnet build "./ReflectYourself.csproj" -c Release -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./ReflectYourself.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "ReflectYourself.dll"]
