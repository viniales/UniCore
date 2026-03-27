import os

# Foldery, których NIE CHCEMY wklejać do AI (żeby nie zapychać pamięci)
IGNORE_DIRS = {'.venv', '.idea', '__pycache__', 'migrations', '.git'}
# Rozszerzenia plików, które nas interesują
ALLOWED_EXTENSIONS = {'.py', '.html'}

output_file = "KOD_DO_PRACY_INZ.txt"

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("STRUKTURA PROJEKTU:\n")

    # Rysowanie struktury katalogów
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace(".", "").count(os.sep)
        indent = " " * 4 * level
        folder_name = os.path.basename(root) if root != "." else "UniCore (Główny folder)"
        outfile.write(f"{indent}{folder_name}/\n")

        subindent = " " * 4 * (level + 1)
        for f in files:
            if any(f.endswith(ext) for ext in ALLOWED_EXTENSIONS) or f == "manage.py":
                outfile.write(f"{subindent}{f}\n")

    outfile.write("\n\n" + "=" * 60 + "\n")
    outfile.write("ZAWARTOSC PLIKOW:\n")
    outfile.write("=" * 60 + "\n")

    # Wklejanie zawartości plików
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS) and file != "wyciagnij_kod.py":
                file_path = os.path.join(root, file)
                outfile.write(f"\n\n--- START PLIKU: {file_path} ---\n\n")
                try:
                    # Tutaj wymuszamy UTF-8, żeby zachować polskie znaki!
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"[Nie udało się odczytać pliku: {e}]\n")
                outfile.write(f"\n--- KONIEC PLIKU: {file_path} ---\n")

print(f"Gotowe! Cały kod zapisano w pliku: {output_file}")