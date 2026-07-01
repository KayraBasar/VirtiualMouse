# 🪄 Sihirli Fare (Magic Mouse) - Hand Tracking Mouse Control

Bu proje, bir web kamerası aracılığıyla el hareketlerinizi takip ederek bilgisayarınızın faresini kontrol etmenizi ve sistem sesini ayarlamanızı sağlayan Python tabanlı bir bilgisayarlı görü (Computer Vision) uygulamasıdır. 

MediaPipe ve OpenCV kütüphaneleri kullanılarak geliştirilmiş olup, donanım gerektirmeden sadece el hareketleriyle sezgisel bir bilgisayar deneyimi sunar.

## 🚀 Özellikler

* **İmleç Kontrolü:** İşaret ve baş parmağınızı birleştirerek fare imlecini ekranda hareket ettirebilirsiniz.
* **Sol ve Sağ Tıklama:** Belirli parmak kombinasyonlarıyla gecikmesiz tıklama işlemleri.
* **Ses Kontrolü:** Elinizi yumruk yapıp bileğinizi sağa veya sola eğerek bilgisayarın ses seviyesini artırıp azaltabilirsiniz.
* **Dinamik Mesafe Algılama:** Elinizin kameraya olan uzaklığına göre parmak uçları arasındaki eşik değerleri otomatik olarak hesaplanır.
* **Gelişmiş Yumuşatma (Smoothing):** İmleç titremelerini önlemek için optimize edilmiş hareket algoritmaları.

---

## 🖐️ Kullanım Kılavuzu (El Hareketleri)

Uygulama çalıştıktan sonra aşağıdaki el hareketleriyle bilgisayarınızı kontrol edebilirsiniz:

| El Hareketi / Pozisyon | Gerçekleşen Eylem |
| :--- | :--- |
| **Baş ve İşaret Parmağı Bitişik** | Fareyi Hareket Ettirme |
| **Baş, İşaret ve Orta Parmak Bitişik** | Sol Tık (Basılı Tutma/Sürükleme dahil) |
| **Baş ve Yüzük Parmağı Bitişik** | Sağ Tık |
| **Yumruk + Sağa Eğik Bilek** | Sesi Artır |
| **Yumruk + Sola Eğik Bilek** | Sesi Azalt |
| **El Açık (Boşta)** | Tıklamaları Serbest Bırakır (Mouse Up) |

---

## 🛠️ Kurulum ve Gereksinimler

Projeyi yerel makinenizde çalıştırmak için sisteminizde **Python 3.x** yüklü olmalıdır. Ayrıca bir web kamerasına ihtiyacınız olacaktır.

**1. Depoyu klonlayın:**
```bash
git clone [https://github.com/KULLANICI_ADIN/sihirli-fare.git](https://github.com/KULLANICI_ADIN/sihirli-fare.git)
cd sihirli-fare
