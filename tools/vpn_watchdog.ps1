# tools/vpn_watchdog.ps1
# چک کردن و ری‌استارت خودکار سرویس‌های WireSock

$Services = @("WireSockAppService", "WireSockConnectService")
$IntervalSec = 120  # هر ۲ دقیقه

Write-Host "[VPN-Watchdog] Started. Monitoring: $($Services -join ', ')"

while ($true) {
    foreach ($ServiceName in $Services) {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if ($service -eq $null) {
            Write-Host "[VPN-Watchdog] $ServiceName not found!"
            continue
        }
        
        if ($service.Status -ne 'Running') {
            Write-Host "[VPN-Watchdog] $ServiceName is $($service.Status). Restarting..."
            try {
                # تلاش برای استارت زدن سرویس
                Start-Service -Name $ServiceName -ErrorAction Stop
                Start-Sleep -Seconds 3
                # بررسی مجدد
                $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
                if ($service.Status -eq 'Running') {
                    Write-Host "[VPN-Watchdog] $ServiceName restarted successfully."
                } else {
                    Write-Host "[VPN-Watchdog] $ServiceName failed to start. Manual check needed."
                }
            } catch {
                Write-Host "[VPN-Watchdog] Error starting ${ServiceName}: $_"
            }
        }
    }
    
    Start-Sleep -Seconds $IntervalSec
}