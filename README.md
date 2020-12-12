# ecb_rss

Scraper RSS czytający kurs walut z Europejskiego Banku Centralnego i zapisujący 
je do bazy danych oraz endpoint wystawiający te dane po REST API.

## Opis

Na projekt składają się dwie niezależne (choć korzystające z jednej bazy danych)
aplikacje:

 - scrapper - pobierający dane z serwera ebc i zapisujący je do bazy danych
 - rest_endpoint - aplikacja django wystawiająca te dane po REST API.

### scrapper

Scrapper pobiera html z adresu https://www.ecb.europa.eu/home/html/rss.en.html 
, wyciąga z niego url-e do feedów rss poszczególnych walut, pobiera dane z
feedów i zapisuje je do bazy. Na końcu przechodzi w stan oczekiwania na 24
godziny. W założeniu więc scrapper ma zostać uruchomiony i pozostawiony samemu 
sobie.

### rest_endpoint

Aplikacja django wystawiająca te dane po REST API. Udostępnia dwa widoki:

 - `/current` - lista walut wraz z najbardziej aktualnymi kursami
 - `/history?name=(skrót waluty np. USD)` - pokazuje jak w czasie zmieniała się 
 wartość waluty

## Uruchomienie

 - utwórz i aktywuj virtualenv (Python3.8)
 - zainstaluj zależności - `pip install -r requirements.txt`
 - wykonaj migracje django - `python manage.py migrate`
 - uruchom scrappera - `python scrapper.py`
 - uruchom rest_endpoint w oddzielnym oknie terminalu - `python manage.py runserver`

## TODO:

 - testy
 - przejście na postgres
 - indeksy na bazie danych
 - info o błedach scrapera
 - informacja że scrapper zadziałał
