#!/usr/bin/env python3
import os
import shutil

print("📁 Копируем build файлы в корень...")

# Копируем все файлы из build в корень
build_dir = "giftpropaganda-frontend/build"
root_dir = "."

for item in os.listdir(build_dir):
    src = os.path.join(build_dir, item)
    dst = os.path.join(root_dir, item)
    
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"📁 Скопирована папка: {item}")
    else:
        shutil.copy2(src, dst)
        print(f"📄 Скопирован файл: {item}")

print("✅ Все файлы скопированы!")
print("📝 Теперь добавьте файлы в git и создайте ветку gh-pages") 