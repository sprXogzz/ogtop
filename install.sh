#!/bin/bash

echo " OGTOP Kurulum Sihirbazı Başlıyor..."

# 1. klasör yolu
PROJECT_DIR=$(pwd)
VENV_PATH="$PROJECT_DIR/.venv"

# 2. python .venv
echo " Sanal ortam hazırlanıyor..."
python3 -m venv .venv
source .venv/bin/activate

# 3. bağımlılıklar 
echo " Kütüphaneler yükleniyor (rich, psutil...)"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install psutil rich pynvml
fi

# 4. alias oluşturma 
echo " Sistem tanımlamaları yapılıyor..."
ALIAS_LINE="alias ogtop='$VENV_PATH/bin/python3 $PROJECT_DIR/monitor.py'"

# Kullanıcının .bashrc dosyasına ekle (Eğer daha önce eklenmemişse)
if ! grep -q "alias ogtop=" ~/.bashrc; then
    echo "$ALIAS_LINE" >> ~/.bashrc
    echo " 'ogtop' komutu ~/.bashrc dosyasına eklendi."
else
    echo " 'ogtop' komutu zaten tanımlı, güncellenmedi."
fi

echo "--------------------------------------------------"
echo " KURULUM TAMAMLANDI"
echo " Değişikliklerin aktif olması için terminali kapatıp açın"
echo "   veya şu komutu çalıştırın: source ~/.bashrc"
echo " Sonrasında herhangi bir klasörde 'ogtop' yazarak başlatabilirsiniz."
echo "--------------------------------------------------"