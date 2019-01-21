# Autor: 
Michał Budnik, nr indeksu 234586

# Opis plików:
 - compiler.py: główny program przetwarzający wejście i wyjście danych kompilatora
 - compiler/lexer.py: program tokenizujący kod wejściowy
 - compiler/parser.py: program tworzący drzewo parsowania, używane jako kod pośredni
 - compiler/errors.py: program wychwytujący podstawowe błędy semantyczne
 - compiler/preoptimiser.py: program wykonujący preoptymalizację kodu (wyliczanie możliwych wartości zmiennych
 - compiler/machine.py: program wykonujący translację drzewa parsowania na kod asemblerowy
 - compiler/postprocessor.py: program przypisujący odpowiednim labelom numery linii, oraz czyszczący kod z komentarzy
 - compiler/__init__.py: plik potrzebny do importu pozostałych plików

# Opis wywołania:
## Wymagania instalacyjne:
 - Python3 w wersji przynajmniej 3.6: Standardowo załączony w systemie Ubuntu. W przypadku nieposiadania należy zainstalować poprzez komendę 'sudo apt-get install python3.6'
 - Python3-distutils: Może się okazać, że potrzebne jest dodatkowe zainstalowanie pakietu distutils poprzez komendę 'apt-get install python3-distutils'
 - Biblioteka Sly: Biblotekę należy pobrać ją ze strony https://github.com/dabeaz/sly, po czym w konsoli przejść do folderu z rozpakowanymi plikami, po czym wywołać komendę 'python3 setup.py install' (alternatywnie biblioteka jest dołączona do kompilatora, należy wtedy wejść do folderu sly-master, po czym wywołać wcześniej przedstawioną komendę)

## Użycie kompilatora:
Obsługa kompilatora następuje poprzez wywołanie komendy:
python3 compiler.py 'file-in' 'file-out'
