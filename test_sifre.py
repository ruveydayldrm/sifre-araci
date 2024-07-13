import unittest

import sifre


class UretmeTesti(unittest.TestCase):
    def test_uzunluk_ve_karakter_turleri(self):
        for _ in range(50):
            s = sifre.sifre_uret(12)
            self.assertEqual(len(s), 12)
            self.assertTrue(any(c in sifre.KUCUK for c in s))
            self.assertTrue(any(c in sifre.BUYUK for c in s))
            self.assertTrue(any(c in sifre.RAKAM for c in s))
            self.assertTrue(any(c in sifre.SEMBOL for c in s))

    def test_secenekler(self):
        s = sifre.sifre_uret(200, sembol=False, rakam=False)
        self.assertTrue(s.isalpha())
        s = sifre.sifre_uret(200, benzerleri_cikar=True)
        self.assertFalse(set(s) & sifre.BENZER)

    def test_her_seferinde_farkli(self):
        self.assertEqual(len({sifre.sifre_uret() for _ in range(100)}), 100)

    def test_cok_kisa(self):
        with self.assertRaises(ValueError):
            sifre.sifre_uret(3)


class DegerlendirmeTesti(unittest.TestCase):
    def puan(self, s):
        return sifre.degerlendir(s)["puan"]

    def test_yaygin_sifreler_cok_zayif(self):
        for s in ["123456", "password", "P@ssw0rd", "Galatasaray1905!", "sifre123", "Qwerty123"]:
            with self.subTest(sifre=s):
                self.assertEqual(self.puan(s), 0)

    def test_zayif_desenler(self):
        self.assertLessEqual(self.puan("aaaaaaaa"), 1)
        self.assertLessEqual(self.puan("abcdefgh"), 1)
        self.assertLessEqual(self.puan("Ali1990"), 1)

    def test_uretilen_sifre_cok_guclu(self):
        self.assertEqual(self.puan(sifre.sifre_uret(16)), 4)

    def test_uzun_kelime_dizisi_guclu(self):
        self.assertGreaterEqual(self.puan("mavi-bisiklet-yagmur-kahve"), 3)

    def test_ardisik_ve_tekrar_sayimi(self):
        self.assertEqual(sifre.ardisik_karakterler("xabcx"), 3)
        self.assertEqual(sifre.ardisik_karakterler("9876"), 4)
        self.assertEqual(sifre.ardisik_karakterler("ab"), 0)
        self.assertEqual(sifre.tekrar_eden_karakterler("xaaaay"), 3)

    def test_oneriler(self):
        oneriler = " ".join(sifre.degerlendir("kedi")["oneriler"])
        self.assertIn("12 karakter", oneriler)
        self.assertIn("büyük harf", oneriler)
        self.assertEqual(sifre.degerlendir("Tq7#mLx9!vR2pW$k")["oneriler"], [])


if __name__ == "__main__":
    unittest.main()
