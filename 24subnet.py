import concurrent.futures
import subprocess
import re

# Список подсетей /24
subnets = [
    "185.225.209.", "92.204.185.", "85.195.98.", "134.119.178.", "92.204.186.", "146.0.250.", "45.63.118.",
    "104.238.166.", "146.0.235.", "92.204.188.", "85.195.92.", "146.0.247.", "146.0.233.", "92.204.187.",
    "173.244.206.", "146.0.230.", "188.42.41.", "46.23.72.", "85.195.116.", "95.179.219.", "45.63.112.",
    "108.61.237.", "185.136.164.", "185.136.167.", "151.106.1.", "24.105.53.", "24.105.54.", "134.119.190.",
    "108.61.122.", "136.244.", "217.69.10.", "92.204.162.", "108.61.176.", "95.179.222.", "95.179.216.",
    "45.77.63.", "108.61.177.", "45.76.45.", "92.204.192.", "23.109.85.", "185.225.209.", "64.95.100.",
    "92.204.193.", "23.109.78.", "92.205.32.", "23.109.142.", "23.109.54.", "23.109.79.", "23.109.77.",
    "92.204.197.", "173.199.113.", "172.255.15.", "74.119.145.", "212.78.82.", "212.84.160.", "95.179.204.",
    "85.195.102.", "78.129.240.", "88.202.177.", "91.109.240.", "45.63.103.", "82.163.76.", "109.123.111.",
    "88.150.230.", "78.129.208.", "78.129.165.", "78.129.185.", "46.28.51.", "212.78.94."
]

temp_file = "temp_result.txt"
sorted_file = "sorted_result.txt"
output_file = "ping_results.txt"
high_ping_file = "high_ping.txt"

def ping(ip):
    try:
        # Выполнение команды ping и получение времени отклика
        result = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True, encoding='cp866')
        print(f"Ping result for {ip}:\n{result.stdout}")  # Отладочная информация

        # Проверка успешности выполнения команды
        if result.returncode == 0:
            # Поиск строки с временем отклика
            match = re.search(r'время=(\d+)', result.stdout)
            if match:
                time = int(match.group(1))
                if time >= 135:
                    with open(temp_file, 'a') as f:
                        f.write(f"{time} - {ip}\n")
                    with open(high_ping_file, 'a') as f:
                        f.write(f"{ip}\n")
                return time, ip
        else:
            with open(temp_file, 'a') as f:
                f.write(f"99999 - {ip} is down\n")
            return None, ip
    except Exception as e:
        with open(temp_file, 'a') as f:
            f.write(f"99999 - {ip} is down\n")
        return None, ip

def create_ip_list(subnets):
    ip_list = []
    for subnet in subnets:
        for i in range(256):
            ip_list.append(f"{subnet}{i}")
    return ip_list

def process_pings():
    ip_list = create_ip_list(subnets)
    
    # Создание пустого файла для записи IP-адресов с высоким пингом
    open(high_ping_file, 'w').close()
    
    # Пингование IP-адресов с использованием многопоточности
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(ping, ip) for ip in ip_list]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    time, ip = result
                    if time is not None:
                        print(f"{time} - {ip}")
                    else:
                        print(f"99999 - {ip} is down")
            except Exception as e:
                print(f"Error: {e}")

    # Сортировка результатов
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    
    # Удаление пустых строк и строк с неправильным форматом
    lines = [line for line in lines if line.strip() and re.match(r'^\d+ -', line)]
    
    lines.sort(key=lambda x: int(x.split()[0]), reverse=True)
    
    with open(sorted_file, 'w') as f:
        f.writelines(lines)
    
    # Запись отсортированных результатов в финальный файл
    with open(sorted_file, 'r') as f:
        lines = f.readlines()
    
    with open(output_file, 'w') as f:
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and parts[0] != "99999":
                f.write(f"{parts[2]} = {parts[0]}\n")
            elif len(parts) >= 3:
                f.write(f"{parts[2]} is down\n")

    # Создание правила блокировки в Windows Firewall для всех IP-адресов с высоким пингом
    with open(high_ping_file, 'r') as f:
        high_ping_ips = f.read().strip().split('\n')
    
    # Разделение IP-адресов на группы по максимуму 100 адресов, чтобы избежать слишком длинных команд
    max_ips_per_rule = 100
    ip_groups = [high_ping_ips[i:i + max_ips_per_rule] for i in range(0, len(high_ping_ips), max_ips_per_rule)]
    
    for i, ip_group in enumerate(ip_groups):
        ip_range = ','.join(ip_group)
        rule_name = f"HighPingServers_{i+1}"
        subprocess.run(f'netsh advfirewall firewall add rule name="{rule_name}" dir=out action=block remoteip={ip_range} enable=yes', shell=True)
        subprocess.run(f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip_range} enable=yes', shell=True)
        print(f"Создано правило брандмауэра '{rule_name}' для блокировки трафика к серверам с высоким пингом: {ip_range}")

    if not high_ping_ips:
        print("Не найдено серверов с высоким пингом для блокировки.")

if __name__ == "__main__":
    process_pings()
