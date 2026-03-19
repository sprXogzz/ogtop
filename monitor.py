import psutil
import time
import socket
import datetime
import os
import signal
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Group, Console
from rich.align import Align

# renk
THEME = {
    "cpu": "bold cyan", "ram": "bold magenta", "disk": "bold yellow",
    "gpu": "bold green", "net": "bold white", "uptime": "bold blue",
    "border": "bright_blue", "title": "OGI SYSTEM MONITOR"
}

console = Console()

def get_uptime():
    boot_time = psutil.boot_time()
    return str(datetime.timedelta(seconds=int(time.time() - boot_time)))

def get_disk_info():
    d = psutil.disk_usage('/')
    return f"%{d.percent} ({d.used // (1024**3)}G/{d.total // (1024**3)}G)"

def get_temp_value():
    """Sıcaklığı sadece sayı (float) olarak döndürür."""
    try:
        temps = psutil.sensors_temperatures()
        for name in ['coretemp', 'cpu_thermal', 'acpitz', 'k10temp']:
            if name in temps: return temps[name][0].current
    except: pass
    return 0.0

def get_temp_str():
    val = get_temp_value()
    return f"{val}°C" if val > 0 else "N/A"

def get_dynamic_logo():
    """Sıcaklığa göre logo altındaki durum yazısını ve rengini değiştirir."""
    temp = get_temp_value()
    
    if temp >= 80:
        status = "CRITICAL: OVERHEATING"
        color = "bold red"
    elif temp >= 65:
        status = "WARNING: HOT"
        color = "bold yellow"
    elif temp >= 45:
        status = "STABLE"
        color = "bold green"
    else:
        status = "OPERATIONAL: COOL"
        color = "bold cyan"

    logo = r"""
[bold cyan]┌────────────────────────────────┐[/bold cyan]
[bold cyan]│   ____   _____ _    _ ______   │[/bold cyan]
[bold cyan]│  / __ \ / ____| |  | |___  /   │[/bold cyan]
[bold cyan]│ | |  | | |  __| |  | |  / /    │[/bold cyan]
[bold cyan]│ | |  | | | |_ | |  | | / /     │[/bold cyan]
[bold cyan]│ | |__| | |__| | |__| |/ /__    │[/bold cyan]
[bold cyan]│  \____/ \_____|\____//_____|   │[/bold cyan]
[bold cyan]└────────────────────────────────┘[/bold cyan]"""
    return f"{logo}\n[{color}]    < SYSTEM STATUS: {status} >[/{color}]"

def get_gpu_info():
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
        return f"GPU: %{util} ({temp}°C)"
    except: return "GPU: N/A"

def get_processes():
    procs = []
    try:
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try: procs.append(p.info)
            except: pass
        top_5 = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        table = Table(expand=True, border_style="dim", box=None)
        table.add_column("PID", style="dim", width=8)
        table.add_column("Uygulama", style=THEME['cpu'])
        table.add_column("CPU %", justify="right")
        for p in top_5:
            table.add_row(str(p['pid']), (p['name'] or "Unknown")[:15], f"{p['cpu_percent']}")
        return table
    except: return "Hata"

def run():
    try: ip = socket.gethostbyname(socket.gethostname())
    except: ip = "127.0.0.1"

    monitor_view = Live(refresh_per_second=2, screen=True)
    
    with monitor_view:
        while True:
            try:
                cpu = psutil.cpu_percent()
                vmem = psutil.virtual_memory()
                
                row1 = Columns([
                    Panel(f"[{THEME['cpu']}]CPU:[/] %{cpu} ({get_temp_str()})", border_style=THEME['border'], expand=True),
                    Panel(f"[{THEME['ram']}]RAM:[/] %{vmem.percent} ({vmem.used//(1024**3)}G/{vmem.total//(1024**3)}G)", border_style=THEME['border'], expand=True),
                    Panel(f"[{THEME['disk']}]DISK:[/] {get_disk_info()}", border_style=THEME['border'], expand=True),
                    Panel(f"[{THEME['uptime']}]UPTIME:[/] {get_uptime()}", border_style=THEME['border'], expand=True)
                ])
                
                row2 = Columns([
                    Panel(f"[{THEME['gpu']}]{get_gpu_info()}[/]", border_style=THEME['border'], expand=True),
                    Panel(f"⬆ {psutil.net_io_counters().bytes_sent/1024/10:.1f} ⬇ {psutil.net_io_counters().bytes_recv/1024/10:.1f} KB/s", border_style=THEME['border'], expand=True)
                ])
                
                main_layout = Group(
                    row1, row2,
                    "\n[bold]TOP PROCESSES[/bold]", get_processes(),
                    "\n", Align.center(get_dynamic_logo()),
                    Align.center(f"[dim]IP: {ip} | [bold red]Ctrl+C: Menu[/bold red][/dim]")
                )
                
                monitor_view.update(Panel(main_layout, title=f"[bold]{THEME['title']}[/bold]", border_style=THEME['border']))
                time.sleep(0.5)

            except KeyboardInterrupt:
                monitor_view.stop() 
                console.print("\n[bold red]─── MONITOR ACTION ───[/bold red]")
                action = console.input("[bold yellow][1][/bold yellow] PID Öldür (Zorla) | [bold yellow][2][/bold yellow] Programdan Çık | [bold cyan][Enter][/bold cyan] Vazgeç: ")
                
                if action == "1":
                    pid_input = console.input("[bold red]Kapatılacak PID (İptal için Enter): [/bold red]")
                    if pid_input.isdigit():
                        try:
                            os.kill(int(pid_input), signal.SIGKILL)
                            console.print(f"[bold green]✔ PID {pid_input} yok edildi![/bold green]")
                            time.sleep(1)
                        except Exception as e:
                            console.print(f"[bold red]❌ Hata: {e}[/bold red]")
                            time.sleep(1.5)
                    monitor_view.start() 
                elif action == "2":
                    break
                else:
                    monitor_view.start() 

if __name__ == "__main__":
    run()