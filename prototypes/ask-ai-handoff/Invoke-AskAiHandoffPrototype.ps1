[CmdletBinding()]
param(
  [ValidateSet('Codex', 'OpenCode')]
  [string]$Execute
)

$prompt = 'Open AIQ Studio and show me the available Rhino workflows.'
$testDirectory = Join-Path $PSScriptRoot 'AIQ-ASK-AI-LAUNCH-TEST'

$null = New-Item -ItemType Directory -Path $testDirectory -Force

$encodedDirectory = [Uri]::EscapeDataString($testDirectory)
$encodedPrompt = [Uri]::EscapeDataString($prompt)

$codexUri = "codex://threads/new?path=$encodedDirectory&prompt=$encodedPrompt"
$openCodeUri = "opencode://new-session?directory=$encodedDirectory&prompt=$encodedPrompt"

Write-Output "Test folder: $testDirectory"
Write-Output "Codex URI: $codexUri"
Write-Output "OpenCode URI: $openCodeUri"
Write-Output ''
Write-Output 'Expected result: The selected desktop app shows the test folder and puts the prompt in the composer.'
Write-Output 'The app must not submit the prompt. Do not press Send during this test.'

if ($Execute) {
  $uri = if ($Execute -eq 'Codex') { $codexUri } else { $openCodeUri }
  Start-Process -FilePath $uri
}
