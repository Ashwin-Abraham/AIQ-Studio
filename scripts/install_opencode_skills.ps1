param([switch]$CheckOnly, [string]$Destination)

$ErrorActionPreference = 'Stop'
$packageRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\plugins\aiq-site-tools\skills')).Path
$installRoot = if ($Destination) { [System.IO.Path]::GetFullPath($Destination) } else { Join-Path ([Environment]::GetFolderPath('UserProfile')) '.config\opencode\skills' }
$skills = @('rhino-site-data-model', 'rhino-to-vector-site-maps')

foreach ($skill in $skills) {
    $source = Join-Path $packageRoot $skill
    $target = Join-Path $installRoot $skill
    if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
        throw "Package is incomplete: $skill"
    }
    if ($CheckOnly) {
        Write-Output "$skill -> $target"
        continue
    }
    $marker = Join-Path $target '.aiq-site-tools-installed'
    if ((Test-Path -LiteralPath $target) -and -not (Test-Path -LiteralPath $marker)) {
        throw "An existing skill uses $target. Leave it in place and choose a different installation location."
    }
    Get-ChildItem -LiteralPath $source -Recurse -File | ForEach-Object {
        $relative = $_.FullName.Substring($source.Length).TrimStart('\', '/')
        $destination = Join-Path $target $relative
        $parent = Split-Path -Parent $destination
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $destination -Force
    }
    Set-Content -LiteralPath $marker -Value 'Installed by AIQ Site Tools' -Encoding utf8
    Write-Output "Installed $skill"
}
if (-not $CheckOnly) {
    Write-Output 'Restart OpenCode to load the skills.'
}
