# Uptime Scheduler – monitor dostępności serwisów WWW
Autor: Bartosz Widlak(link do gh)

## Instalacja
Opis instalacji

## Uzyte biblioteki
Opis bibliotek i ich zastosowania w skrypcie
- [*aiohttp*](https://asd.pl) - biblioteka obsługująca zapytania do serwerów
- [*colorama*](https://adsd.pl) - biblioteka pozwalająca na kolorowe pisanie w konsoli
## Opis funkcji
Lista funkcji i ich zastosownianie, argumenty

1. open_config(path_to_config) - funkcja otwierająca config w formacie json, sprawdza molzliwość otwarcia pliku oraz jego poprawna składnie. Zwraca JSON.

2. load_config(json) - Sprawdza typ poszczególnych wartość, w przypadku ich braku ustawia domyślne wartości.
## Opis pliku konfiguracyjnego
Opis pliku konfiguracyjnego

## Problemy
Czesc stron (np. https://oracle.com, https://www.amazon.pl) potrafia rzucic status 403 - forbiden lub 503 - service unaviable mimo ze w przegladarce jestesmy w stanie poprawnie wlaczyc dana strone
## Ograniczenia

## Potencjalne ulepszenia
