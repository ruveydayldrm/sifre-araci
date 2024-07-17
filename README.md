# Şifre Aracı 🔐

Güçlü ve rastgele şifreler üreten, var olan bir şifrenin ne kadar güçlü olduğunu puanlayan küçük bir Python aracı.

```
$ python sifre.py kontrol
Şifre (ekranda görünmez):
Güç: ██░░░  Zayıf (≈31 bit)
  • En az 12 karakter kullanın.
  • Yıl ya da doğum tarihi kullanmayın.
```

## Özellikler

**Üretme**
- Python'un `secrets` modülüyle kriptografik olarak güvenli rastgelelik
- Seçilen her karakter türünden (küçük, büyük, rakam, sembol) en az bir tane garanti
- `--benzerleri-cikar`: `I l 1 O 0` gibi birbirine karışan karakterleri kullanmaz

**Kontrol**
- 0–4 arası puan: Çok zayıf → Çok güçlü, tahmini bit gücüyle birlikte
- Yaygın şifreleri yakalar; `P@ssw0rd`, `sifre123!` gibi hâlleri de dahil (Türkçe liste içerir)
- `abc`, `123`, `qwerty` gibi ardışık karakterleri, tekrarları ve yılları tespit eder
- Neyin eksik olduğunu Türkçe önerilerle söyler
- Şifre gizli olarak sorulur; ekranda ve komut geçmişinde görünmez

Ek kütüphane gerektirmez; yalnızca Python 3.9+. İnternete hiçbir şey göndermez.

## Kullanım

```bash
python sifre.py uret                          # 16 karakter
python sifre.py uret -u 24 -a 5               # 24 karakterlik 5 şifre
python sifre.py uret --sembolsuz --benzerleri-cikar
python sifre.py kontrol                       # Şifreyi gizli sorar
```

> Puanlama tahminidir; gerçek dünyadaki saldırıların tamamını modellemez. Her hesap için farklı şifre ve bir şifre yöneticisi kullanmanız önerilir.

## Testler

```bash
python -m unittest -v
```
