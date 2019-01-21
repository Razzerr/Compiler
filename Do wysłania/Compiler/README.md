## Autor: 
Michał Budnik, nr indeksu 234586

##Opis plików:
 - compiler.py: główny program przetwarzający wejście i wyjście danych kompilatora
 - compiler/lexer.py: program tokenizujący kod wejściowy
 - compiler/parser.py: program tworzący drzewo parsowania, używane jako kod pośredni
 - compiler/errors.py: program wychwytujący podstawowe błędy semantyczne
 - compiler/preoptimiser.py: program wykonujący preoptymalizację kodu (wyliczanie możliwych wartości zmiennych
 - compiler/machine.py: program wykonujący translację drzewa parsowania na kod asemblerowy
 - compiler/postprocessor.py: program przypisujący odpowiednim labelom numery linii, oraz czyszczący kod z komentarzy
 - compiler/__init__.py: plik potrzebny do importu pozostałych plików

##Opis wywołania:
#Wymagania instalacyjne:
 - Python3: Standardowo załączony w systemie Ubuntu. W przypadku nieposiadania należy ściągnąć najnowszą wersję ze strony https://www.python.org/downloads/
 - Biblioteka Sly: 
