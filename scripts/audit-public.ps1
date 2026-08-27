param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$patterns = @(
    '(?i)(api[_-]?key|secret|password|bearer|authorization|access[_-]?token)',
    'sk-[A-Za-z0-9_-]{16,}',
    'AKIA[0-9A-Z]{16}',
    'gh[pous]_[A-Za-z0-9_]{20,}',
    'xox[baprs]-[A-Za-z0-9-]{10,}',
    '(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}',
    '(?i)(C:|/Users/|/home/)[^\\s]+'
)

$files = Get-ChildItem -Path $RepositoryRoot -Recurse -File -Force |
    Where-Object {
        $_.FullName -notmatch '[\\/]\.git[\\/]' -and
        $_.FullName -notmatch '[\\/](pending|private|secrets|\.secrets)[\\/]'
    }

$matches = foreach ($pattern in $patterns) {
    $files | Select-String -Pattern $pattern -ErrorAction SilentlyContinue
}

if ($matches) {
    $matches | Select-Object Path, LineNumber, Line | Format-Table -AutoSize
    throw 'Public-release audit failed. Remove or explicitly review every match before publishing.'
}

Write-Host 'Public-release audit passed: no common credential, email, or local-path pattern found.'
