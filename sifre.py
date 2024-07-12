#!/usr/bin/env python3
"""Şifre Aracı — güçlü şifre üretir ve bir şifrenin ne kadar güçlü olduğunu puanlar.

Kullanım:
    python sifre.py uret                     # 16 karakterlik şifre
    python sifre.py uret -u 24 -a 5          # 24 karakterlik 5 şifre
    python sifre.py kontrol                  # Şifreyi gizli olarak sorar
"""

from __future__ import annotations

import argparse
import getpass
import math
import re
import secrets
import string
import sys

KUCUK = string.ascii_lowercase
BUYUK = string.ascii_uppercase
RAKAM = string.digits
SEMBOL = "!@#$%^&*()-_=+[]{};:,.?/"
BENZER = set("Il1|O0o")
EN_KISA = 4

ETIKETLER = ["Çok zayıf", "Zayıf", "Orta", "Güçlü", "Çok güçlü"]
SINIRLAR = [28, 40, 60, 80]  # bit cinsinden puan eşikleri

YAYGIN = {
    "123456", "1234567", "12345678", "123456789", "1234567890", "111111", "000000", "123123",
    "password", "qwerty", "qwerty123", "abc123", "iloveyou", "admin", "letmein", "welcome",
    "monkey", "dragon", "sifre", "şifre", "parola", "asdasd", "asd123", "qwe123", "1q2w3e",
    "1q2w3e4r", "galatasaray", "fenerbahce", "fenerbahçe", "besiktas", "beşiktaş", "trabzonspor",
    "istanbul", "ankara", "turkiye", "türkiye", "seniseviyorum", "merhaba",
}
SIRALAR = ["abcdefghijklmnopqrstuvwxyz", "0123456789", "qwertyuiop", "asdfghjkl", "zxcvbnm"]
LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})


# --- Üretme ------------------------------------------------------------------

def sifre_uret(uzunluk: int = 16, buyuk: bool = True, rakam: bool = True,
               sembol: bool = True, benzerleri_cikar: bool = False) -> str:
    """Kriptografik olarak güvenli rastgele şifre üretir; seçilen her
    karakter türünden en az bir tane içermesi garanti edilir."""
    gruplar = [KUCUK] + [g for g, secili in ((BUYUK, buyuk), (RAKAM, rakam), (SEMBOL, sembol)) if secili]
    if benzerleri_cikar:
        gruplar = ["".join(c for c in g if c not in BENZER) for g in gruplar]
    if uzunluk < max(EN_KISA, len(gruplar)):
        raise ValueError(f"Şifre en az {max(EN_KISA, len(gruplar))} karakter olmalı.")

    karakterler = [secrets.choice(g) for g in gruplar]
    havuz = "".join(gruplar)
    karakterler += [secrets.choice(havuz) for _ in range(uzunluk - len(karakterler))]
    secrets.SystemRandom().shuffle(karakterler)
    return "".join(karakterler)


# --- Değerlendirme -----------------------------------------------------------

def havuz_boyutu(sifre: str) -> int:
    boyut = 0
    if any(c in KUCUK for c in sifre):
        boyut += 26
    if any(c in BUYUK for c in sifre):
        boyut += 26
    if any(c in RAKAM for c in sifre):
        boyut += 10
    if any(not c.isascii() and c.isalpha() for c in sifre):
        boyut += 12  # ç, ğ, ı, ö, ş, ü ve büyükleri
    if any(c.isascii() and not c.isalnum() for c in sifre):
        boyut += 33
    return max(boyut, 1)


def ardisik_karakterler(sifre: str) -> int:
    """'abc', '321', 'qwer' gibi en az 3 uzunluktaki dizilerdeki karakter sayısı."""
    s = sifre.lower()

    def yonler(ikili):
        # Bu iki karakterin hangi dizide, hangi yönde ardışık olduğu
        return {(k, 1) for k, sira in enumerate(SIRALAR) if ikili in sira} | \
               {(k, -1) for k, sira in enumerate(SIRALAR) if ikili[::-1] in sira}

    toplam, i = 0, 0
    while i < len(s) - 1:
        ortak = yonler(s[i:i + 2])
        j = i + 1
        while ortak and j + 1 < len(s) and ortak & yonler(s[j:j + 2]):
            ortak &= yonler(s[j:j + 2])
            j += 1
        if ortak and j - i + 1 >= 3:
            toplam += j - i + 1
        i = j
    return toplam


def tekrar_eden_karakterler(sifre: str) -> int:
    """'aaa', '1111' gibi 3+ tekrarlarda ilki dışındaki karakter sayısı."""
    return sum(len(m.group(0)) - 1 for m in re.finditer(r"(.)\1{2,}", sifre))


def yaygin_mi(sifre: str) -> bool:
    """Yaygın şifreleri, harf yerine rakam kullanılmış (p@ssw0rd) ya da sonuna
    sayı/sembol eklenmiş (sifre123!) hâlleriyle birlikte yakalar."""
    kucuk = sifre.lower()
    adaylar = {kucuk, kucuk.translate(LEET)}
    adaylar |= {re.sub(r"[\d\W_]+$", "", a) for a in list(adaylar)}
    adaylar |= {re.sub(r"^[\d\W_]+", "", a) for a in list(adaylar)}
    return bool(adaylar & YAYGIN)


def degerlendir(sifre: str) -> dict:
    """Şifrenin tahmini gücünü bit olarak hesaplar, 0-4 arası puan ve öneriler döner."""
    havuz = havuz_boyutu(sifre)
    karakter_basi = math.log2(havuz)
    oneriler = []

    zayif = ardisik_karakterler(sifre) + tekrar_eden_karakterler(sifre)
    yillar = re.findall(r"(?:19|20)\d\d", sifre)
    zayif = min(len(sifre), zayif + 4 * len(yillar))
    # Tahmin edilebilir karakterler yalnızca 1 bit katkı sağlar
    bit = (len(sifre) - zayif) * karakter_basi + zayif

    if yaygin_mi(sifre):
        bit = min(bit, 10)
        oneriler.append("Bu şifre (ya da benzeri) en yaygın şifreler listesinde, hemen değiştirin.")
    if len(sifre) < 12:
        oneriler.append("En az 12 karakter kullanın.")
    if ardisik_karakterler(sifre):
        oneriler.append("'abc', '123', 'qwe' gibi ardışık karakterlerden kaçının.")
    if tekrar_eden_karakterler(sifre):
        oneriler.append("Aynı karakteri art arda tekrarlamayın.")
    if yillar:
        oneriler.append("Yıl ya da doğum tarihi kullanmayın.")
    eksik = [ad for ad, grup in (("büyük harf", BUYUK), ("rakam", RAKAM)) if not any(c in grup for c in sifre)]
    if not any(c.isascii() and not c.isalnum() for c in sifre):
        eksik.append("sembol")
    if eksik and len(sifre) < 20:
        oneriler.append(f"Şunları ekleyin: {', '.join(eksik)}.")

    puan = sum(bit >= s for s in SINIRLAR)
    return {"puan": puan, "etiket": ETIKETLER[puan], "bit": round(bit, 1), "oneriler": oneriler}


# --- Komut satırı ------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sifre", description="Güçlü şifre üretir ve şifre gücünü ölçer.")
    alt = p.add_subparsers(dest="komut", required=True)

    u = alt.add_parser("uret", help="Rastgele şifre üret")
    u.add_argument("-u", "--uzunluk", type=int, default=16, help="Karakter sayısı (varsayılan: 16)")
    u.add_argument("-a", "--adet", type=int, default=1, help="Kaç şifre üretilecek")
    u.add_argument("--buyuksuz", action="store_true", help="Büyük harf kullanma")
    u.add_argument("--rakamsiz", action="store_true", help="Rakam kullanma")
    u.add_argument("--sembolsuz", action="store_true", help="Sembol kullanma")
    u.add_argument("--benzerleri-cikar", action="store_true", help="I, l, 1, O, 0 gibi karışan karakterleri kullanma")

    k = alt.add_parser("kontrol", help="Şifre gücünü ölç")
    k.add_argument("sifre", nargs="?", help="Boş bırakılırsa gizli olarak sorulur (önerilen)")

    args = p.parse_args(argv)

    if args.komut == "uret":
        try:
            for _ in range(max(1, args.adet)):
                print(sifre_uret(args.uzunluk, not args.buyuksuz, not args.rakamsiz,
                                 not args.sembolsuz, args.benzerleri_cikar))
        except ValueError as h:
            print(f"Hata: {h}", file=sys.stderr)
            return 1
        return 0

    sifre = args.sifre
    if sifre is None:
        sifre = getpass.getpass("Şifre (ekranda görünmez): ")
    else:
        print("Not: Komut satırına yazılan şifre geçmişte kalabilir; argümansız kullanmanız daha güvenli.\n")
    if not sifre:
        print("Şifre boş.", file=sys.stderr)
        return 1

    sonuc = degerlendir(sifre)
    cubuk = "█" * (sonuc["puan"] + 1) + "░" * (4 - sonuc["puan"])
    print(f"Güç: {cubuk}  {sonuc['etiket']} (≈{sonuc['bit']:.0f} bit)")
    for oneri in sonuc["oneriler"]:
        print(f"  • {oneri}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
