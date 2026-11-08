import os, time, subprocess, sys
import psutil  # برای چک کردن پروسه‌ها

def is_runner_alive(script_name):
    """چک می‌کند آیا پروسه پایتونی با این اسم در حال اجراست یا نه."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # بررسی می‌کنیم آیا در دستور اجرای پروسه، اسم اسکریپت وجود دارد
            if proc.info['name'] == 'python.exe' and proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def start_runner(script_path):
    print(f"[Auto-Restart] Starting {script_path}...")
    subprocess.Popen(["python", script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    print("[Auto-Restart] Process-based monitoring started. Checking every 5 minutes...")
    while True:
        # چک کردن فیوچرز
        if not is_runner_alive("futures_strategy_runner.py"):
            print("[Auto-Restart] Futures runner is NOT running. Restarting...")
            start_runner("tools\\futures_strategy_runner.py")
        
        # چک کردن اسپات
        if not is_runner_alive("spot_runner.py"):
            print("[Auto-Restart] Spot runner is NOT running. Restarting...")
            start_runner("tools\\spot_runner.py")

        time.sleep(300)  # هر ۵ دقیقه چک می‌کند

if __name__ == "__main__":
    main()