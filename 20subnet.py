import concurrent.futures
import subprocess
import re

# Список подсетей /20
subnets = [
    "146.0.240.", "151.106.48.","107.6.160."  # Подсеть /20
    # Добавьте другие подсети /20 по мере необходимости
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
        print(f"Exception while pinging {ip}: {e}")
        with open(temp_file, 'a') as f:
            f.write(f"99999 - {ip} is down\n")
        return None, ip

def create_ip_list(subnets):
    ip_list = []
    for subnet in subnets:
        base = subnet.split('.')
        for i in range(16):
            for j in range(256):
                ip_list.append(f"{base[0]}.{base[1]}.{int(base[2])+i}.{j}")
    return ip_list

def process_pings():
    ip_list = create_ip_list(subnets)
    
    # Создание пустого файла для записи IP-адресов с высоким пингом
    open(high_ping_file, 'w').close()
    
    # Пингование IP-адресов с использованием многопоточности
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:  # Уменьшите количество потоков при необходимости
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
                print(f"Error in future result: {e}")

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
    
    if high_ping_ips:
        chunk_size = 200
        chunks = [high_ping_ips[i:i + chunk_size] for i in range(0, len(high_ping_ips), chunk_size)]
        rule_number = 1
        for chunk in chunks:
            ips = ','.join(chunk)
            rule_name = f"HighPingServersApex/20_{rule_number}"
            try:
                subprocess.run(f'netsh advfirewall firewall add rule name="{rule_name}" dir=out action=block remoteip={ips} enable=yes', shell=True, check=True)
                subprocess.run(f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ips} enable=yes', shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error creating firewall rule {rule_name}: {e}")
            rule_number += 1
        print(f"Создано {rule_number - 1} правил(о) брандмауэра для блокировки трафика к серверам с высоким пингом.")
    else:
        print("Не найдено серверов с высоким пингом для блокировки.")

if __name__ == "__main__":
    process_pings()
