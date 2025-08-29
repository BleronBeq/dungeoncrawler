import os

def count_loc(directory, extensions=(".py",)):
    total_lines = 0
    for dirpath, _, filenames in os.walk(directory):
        for file in filenames:
            if file.endswith(extensions):
                with open(os.path.join(dirpath, file), encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                    total_lines += len(code_lines)
    return total_lines

path = r"C:\Users\Admin\OneDrive\Desktop\VS-Code Uni\Python\Skriptsprachen\Code"
print(f"Lines of Code: {count_loc(path)}")
