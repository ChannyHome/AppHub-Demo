$scheme = "apphub"
$base   = "HKLM:\SOFTWARE\Classes\$scheme"

New-Item $base -Force | Out-Null
Set-ItemProperty $base -Name "(default)" -Value "URL:AppHub Protocol"
New-ItemProperty $base -Name "URL Protocol" -Value "" -Force | Out-Null

New-Item "$base\shell\open\command" -Force | Out-Null
Set-ItemProperty "$base\shell\open\command" -Name "(default)" `
    -Value '"C:\Program Files (x86)\AppHubAgent\Agent\AppHubAgent.exe" "%1"'
