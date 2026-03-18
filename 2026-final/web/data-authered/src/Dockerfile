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
RUN cd DataAuthered && $HOME/.dotnet/tools/libman restore
RUN dotnet build "./DataAuthered/DataAuthered.csproj" -c Release -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./DataAuthered/DataAuthered.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

ENV FLAG="SSM{you_authered_the_data!!}"
ENV Logging__LogLevel__Microsoft.AspNetCore.DataProtection.Repositories=None

ENTRYPOINT ["dotnet", "DataAuthered.dll"]
