# Entropy Analyzer

Az **Entropy Analyzer** egy Python-alapú grafikus alkalmazás, amely fájlok entrópiáját képes kiszámítani és vizualizálni. Az entrópia elemzése hasznos lehet például titkosított, tömörített vagy strukturált adatok azonosítására, adatforenzikai célokra, vagy csak a fájlszerkezet megértésére.

## Főbb jellemzők

- Shannon-entrópia számítása csúszó ablakokkal
- Interaktív grafikon (matplotlib)
- Több fájl egyidejű vizsgálata
- Színkódolt entrópia-sávok a vizuális értelmezéshez
- Magyar és angol nyelvű felhasználói felület
- Beépített súgó
- PNG / SVG mentési lehetőség

## Telepítés

1. Klónozd vagy töltsd le a repót.
2. Telepítsd a szükséges csomagokat:
   ```bash
   pip install -r requirements.txt
   ```
3. Futtasd a programot:
   ```bash
   python "entropy analyzer.py"
   ```

## Használat

1. Indítás után válassz ki egy könyvtárat a fájlokkal.
2. Jelölj ki egy vagy több fájlt a listából.
3. Add meg az entrópia számításhoz használt ablakméretet bájtban.
4. Kattints a „Fájlok betöltése” gombra.
5. Vizsgáld meg az interaktív grafikont, mentsd el az eredményeket.

További információ a beépített súgóban érhető el a programon belül.

## Függőségek

- Python 3.6+
- numpy
- matplotlib
- tkinter (általában a Python része)

## Licenc

Ez a projekt szabadon használható, szerkeszthető és továbbfejleszthető.
