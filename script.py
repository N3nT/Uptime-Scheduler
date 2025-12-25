import time
import aiohttp
import asyncio
from colorama import Fore, Style
import json
import datetime
import sys

#consts
DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_LOG_PATH = "log.txt"

def load_paths_from_args() -> tuple[str, str]:
    """Funkcja przyjmuje podane przy wywolaniu skryptu sciezki do pliku konfiguracyjnego i pliku z logami"""
    args = sys.argv[1:]

    if len(args) >= 1 and isinstance(args[0], str):
        config_path = args[0]
    else:
        print(Fore.YELLOW + "Nie podano sciezki do pliku konfiguracyjnego, domyslna sciezka: config.json" + Style.RESET_ALL)
        config_path = DEFAULT_CONFIG_PATH

    if len(args) >= 2 and isinstance(args[1], str):
        log_path = args[1]
    else:
        print(Fore.YELLOW + "Nie podano sciezki do pliku z logami, domysla sciezka: log.txt" + Style.RESET_ALL)
        log_path = DEFAULT_LOG_PATH

    return config_path, log_path


def open_config(path_to_config: str) -> dict:
    """Funkcja sprawdza mozliwość otwarcia pliku konfiguracyjnego, oraz mozliwość skonwertowania go z pliku json do obiektu python"""
    try:
        with open(path_to_config, "r", encoding="utf-8") as config:
            data = json.load(config)
    except FileNotFoundError:
        print(Fore.RED + "Nie znaleziono pliku" + Style.RESET_ALL)
        raise
    except PermissionError:
        print(Fore.RED + "Nie poprawne uprawnienia dla pliku" + Style.RESET_ALL)
        raise
    except json.JSONDecodeError:
        print(Fore.RED + "Niepoprawny format pliku JSON" + Style.RESET_ALL)
        raise
    else:
        return data


def check_url(url: str) -> bool:
    """Sprawdza poprawnosc podanego url, np. 'https://domena.pl' lub 'http://192.168.0.1'"""
    if not isinstance(url, str):
        return False
    if not url.startswith(("https://", "http://")):
        return False
    return True


def load_config(data: dict) -> dict:
    """Sprawdza istnienie danych kluczy potrzebnych do konfiguracji dzialania programu, w razie ich braku ustawia wartosci domyslne"""
    urls = data.get("urls", [])
    if not isinstance(urls, list):
        print(Fore.YELLOW + "'urls' powinno byc lista - ignoruje" + Style.RESET_ALL)
        urls = []

    timeout = data.get("timeout", 5.0)
    if not isinstance(timeout, float):
        try:
            timeout = float(timeout)
        except (ValueError, TypeError):
            print(Fore.YELLOW + "'timeout' powinno byc float - uzywam domyslnego 5.0" + Style.RESET_ALL)
            timeout = 5.0

    interval = data.get("interval", 5)
    if not isinstance(interval, int):
        print(Fore.YELLOW + "'interval' powinno byc intem - uzywam domyslnego 5" + Style.RESET_ALL)
        interval = 5

    should_save_to_file = data.get("should_save_to_file", True)
    if not isinstance(should_save_to_file, bool):
        print(Fore.YELLOW + "'should_save_to_file' powinno byc bool - uzywam domyslnego True" + Style.RESET_ALL)
        should_save_to_file = True

    should_print_to_console = data.get("should_print_to_console", True)
    if not isinstance(should_print_to_console, bool):
        print(Fore.YELLOW + "'should_print_to_console' powinno byc bool - uzywam domyslnego True" + Style.RESET_ALL)
        should_print_to_console = True

    today = str(datetime.date.today().weekday())
    schedule = data.get("schedule", {})
    if not isinstance(schedule, dict):
        print(Fore.YELLOW + "'schedule' powinno byc slownikiem - ignoruje" + Style.RESET_ALL)
        schedule = {}

    today_urls = schedule.get(today, [])
    if not isinstance(today_urls, list):
        print(Fore.YELLOW + "'today_urls' powinno byc lista - ignoruje" + Style.RESET_ALL)
        today_urls = []

    final_urls = set(urls + today_urls)
    clean_urls = []

    for url in final_urls:
        if isinstance(url, str) and check_url(url):
            clean_urls.append(url)
        else:
            print(Fore.RED + f"Nieprawidłowy URL: {url}" + Style.RESET_ALL)

    final_urls = clean_urls

    return {
        "urls": final_urls,
        "timeout": timeout,
        "interval": interval,
        "should_save_to_file": should_save_to_file,
        "should_print_to_console": should_print_to_console
    }


def convert_http_status(http_status: str) -> str:
    """Przypisuje danemu statusowi http status UP lub DOWN"""
    if isinstance(http_status, int):
        return "UP" if 200 <= http_status <= 399 else "DOWN"
    else:
        return http_status


def prepare_message(url: str, status: str, time_to_answer: float, end_time) -> str:
    """W zaleznosci od statusu przygotowuje wiadomosc gotowa do wypisania na konsoli, lub zapisania w pliku"""
    date_and_time = end_time.strftime("%d/%m/%Y, %H:%M:%S")
    status = convert_http_status(status)

    if status == "DOWN" or status == "TIMEOUT":
        time_to_answer = "-" * 6
    else:
        time_to_answer = f"{time_to_answer:.3f}s"

    return f"{date_and_time} | {url:<50} | {status:<12} | {time_to_answer}"


def print_info(url: str, status: str, time_to_answer: float, end_time):
    """Wypisuje wiadomosc przygotowana przez prepare_message, w zaleznosci od statusu zmienia kolor czionki w konsoli"""
    if status == "DOWN":
        color = Fore.RED
    elif status == "TIMEOUT":
        color = Fore.YELLOW
    else:
        color = Fore.GREEN

    print(color + prepare_message(url, status, time_to_answer, end_time) + Style.RESET_ALL)


def check_log_file(file_path: str):
    """Sprawdza istnienie i uprawnienia do pliku, jezeli plik jest pusty dopisuje na gorze legende"""
    try:
        with open(file_path, "a+") as f:
            f.seek(0)
            if len(f.readlines()) == 0:
                f.write(f"{'Data':<20} | {'URL':<50} | {'Status':<12} | {'Latency':<15}\n")
                f.write("-" * 98 + "\n")
    except FileNotFoundError:
        print(f"Brak bliku w sciezce {file_path}")
        raise
    except PermissionError:
        print(f"Brak uprawnien do odczytu i modyfikacji pliku o sciezce {file_path}")
        raise


def save_to_file(file_path: str, url: str, status: str, time_to_answer: float, end_time):
    """Funkcja odpowiedzialna za zapisywanie do pliku przygotowanej przez funkcje prepare_message wiadomosci"""
    with open(file_path, "a+") as f:
        f.write(prepare_message(url, status, time_to_answer, end_time) + "\n")


def save_to_json(results: list[tuple]):
    """Funkcja zapisuje wyniki w formacie json w pliku data.json"""
    data = {
        "meta":{
            "generated_at": f"{datetime.datetime.now().isoformat()}"
        },
        "results": []
    }
    for result in results:
        url, status, time_to_answer, end_time = result
        new_record = {
            "url": url,
            "status": status,
            "time_to_answer": time_to_answer,
            "time": end_time.isoformat()
        }

        data["results"].append(new_record)

    with open("data.json", "w+") as f:
        json.dump(data, f, indent=2)


async def fetch(session: aiohttp.ClientSession, url: str, timeout: float):
    """Funkcja sprawdzajaca polaczenie z podanym url, zwraca odpowiedni status oraz czas reakcji serwera"""
    start = time.perf_counter()
    try:
        async with session.get(url, timeout=timeout) as resp:
            status = resp.status

    except asyncio.TimeoutError:
        status = "TIMEOUT"

    except aiohttp.ClientError:
        status = "DOWN"
    end_time = datetime.datetime.now()
    latency = time.perf_counter() - start
    return url, status, latency, end_time


async def check_all(urls: list, session: aiohttp.ClientSession, timeout: float):
    """Asynchroniczna funkcja wykonujaca zapytania do wszystkich url i zbierajaca wyniki tych zapytan"""
    tasks = [fetch(session, url, timeout) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


def output_results(should_print_to_console, should_save_to_file, log_path, result):
    """Funkcja jest odpowiedzialna za przekazywanie wynikow w odpowiednie miejsce (konsola / plik)"""
    url, status, time_to_answer, end_time = result
    status = convert_http_status(status)
    if should_print_to_console:
        print_info(url, status, time_to_answer, end_time)
    if should_save_to_file:
        save_to_file(log_path, url, status, time_to_answer, end_time)


async def main(config_path: str, log_path: str):
    """Glowna funkcja tworzaca sesje, w petli laczy wszystkie funkcje w spojna calosc, dziala w zaleznosci od parametru run"""
    async with aiohttp.ClientSession() as session:
        prev_save_state = False
        while not stop_event.is_set():
            try:
                json_data = open_config(config_path)
                config = load_config(json_data)

                #sprawdzenie czy inicjalizacja pliku logow, tylko jezeli zmieni sie config
                if config["should_save_to_file"] and not prev_save_state:
                    check_log_file(log_path)

                prev_save_state = config["should_save_to_file"]

                results = await check_all(config["urls"], session, config["timeout"])
                sorted_results = sorted(results, key=lambda x: x[3]) #x[3] = end_time
                save_to_json(sorted_results)
                for result in sorted_results:
                    output_results(config["should_print_to_console"], config["should_save_to_file"], log_path, result)
                await asyncio.sleep(config["interval"])

            except asyncio.CancelledError:
                break


if __name__ == '__main__':
    stop_event = asyncio.Event()
    cfg, log = load_paths_from_args()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main(cfg, log))
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nZakończenie po bieżącej iteracji..." + Style.RESET_ALL)
        stop_event.set()
        loop.run_until_complete(task)
