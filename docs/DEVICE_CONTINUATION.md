# Cihaz değiştirerek aynı proje noktasından devam

Gate 0'ın kayıtlı MACM6 referans/hazırlık işleri tamamlandı. Gate 0'ın genel
hedefinde yer alan iki yayın benchmark'ının tamamlanmış kaydı henüz yok:
makalenin bölüm 9'undaki homojen tetikleme ODE sistemi ve bölüm 11.4'ündeki
indirgenmiş pertürbasyon/büyüme sistemi. Bunlar yayınlanan örnek parametrelerle
RTX5070 sonucu beklemeden MACM6'da yeniden üretilebilir. Henüz ayrı görev/ayar/
rapor olarak kaydedilmediler. Kapalı üretim kozmolojisi veya tam Boltzmann kabulü
yerine geçmezler. Ayrıntı: `docs/G0_MACM6_REMAINING.md`.

GPU çıktısı olmadan ek olarak kolektif modların analitik kataloğu, küçük örneklerde özdeğer çözücüsü
doğrulaması ve üretim hesaplarını kaydedip sürdürme desteği hazırlanabilir.
Bu ek işler henüz yapılmadı; özgün durağan dizi/fiziksel spektrum gate'lerini
kapatmaz. RTX5070 için acil bir çalıştırma zorunluluğu yok. Gate 0 kapanışı için
ilk gerçek RTX5070 işi G0A-T02, sonra G0B-T01/T02 ve G0B-T03/T04'tür.

## Şu anda neler korunuyor?

- Git bundle: kod, ayarlar, raporlar, küçük çalışma kayıtları ve commit geçmişi.
- `state/state.yaml`: görevler, cihazların tamamlanma kutuları ve erteleme kararı.
- `NEXT.md` ve `MACHINE_HANDOFF.md`: tek sıradaki iş ve kısa devir notu.
- Exact kaynak `yayınlanan.pdf` ve hash ile kimliği belirlenen HDF5 alanı.

HDF5 dosyası bağımsız, **durağan olmayan bir başlangıç alanıdır**. Hesap
iterasyonunun ortasından devam için optimizer/L-BFGS geçmişi, AL çarpanı,
iterasyon sayacı ve RNG durumunu birlikte kaydeden üretim checkpoint desteği
henüz yok. Mevcut paket, tamamlanan alt adımlar arasındaki proje devamını sağlar.

## En pratik geçiş

1. Son doğrulanmış RTX5070 ZIP'ini diğer bilgisayara USB veya dosya aktarımıyla taşı.
2. ZIP'i yeni bir klasöre çıkar. Bu klasörde `REPOSITORY.bundle`, `TRANSFER.json`,
   `yayınlanan.pdf`, `checkpoints/` ve bu başlangıç rehberi bulunur.
3. Çıkardığın klasörü Codex'te proje olarak aç ve aşağıdaki mesajı gönder.
   Paket geri yüklendikten sonra kalıcı proje klasörü `repo/` olur.
4. Sonraki oturumlarda `repo/` klasörünü aç; AGENTS/NEXT/devir notundan devam et.

Başlangıç mesajı:

> Bu klasör MACM6'dan gelen RTX5070 aktarım paketidir. Önce TRANSFER.json'u oku
> ve listelenen dosyaların SHA256 değerlerini doğrula. REPOSITORY.bundle içindeki
> belirtilen branch'i yeni repo/ alt klasörüne clone et; yayınlanan.pdf ve
> checkpoints/ içeriğini yollarını koruyarak oraya kopyala. Var olan başka bir
> repo varsa üzerine yazma. Commit'in manifest ile aynı olduğunu doğrula.
> Ardından repo/AGENTS.md, repo/NEXT.md, repo/MACHINE_HANDOFF.md ve orada belirtilen
> raporları oku. Şimdi RTX5070 cihazındayım ve devam edilmesini istiyorum.
> Bu cihazın Python 3.12/CUDA ortamını hazırla, gerçek GPU'yu kontrol et,
> RTX5070 ertelemesini kaldır ve G0A-T02'den devam et. Tamamlanan MACM6 işlerini
> tekrarlama; yalnız gerçek RTX5070 sonuçlarıyla onun kutusunu işaretle.
> STATUS'u bu cihazın klasör yollarıyla yeniden üret. CLOUD kapalı kalsın.

İlk geri yükleme için Git gerekir; GPU kabulü için Python 3.12, gerçek CUDA
ortamı ve uygun PyTorch kurulumu gerekir. MACM6'nın `.venv` klasörü taşınmaz.
Kurulum/uyumluluk hedef RTX5070 cihazında doğrulanır; MACM6 bunu onaylamış değildir.

El ile geri yükleme gerekirse, ZIP'in çıkarıldığı klasörde:

```sh
git clone -b codex/macm6-completion REPOSITORY.bundle repo
```

Sonra `yayınlanan.pdf` ve `checkpoints/` klasörünü `repo/` içine kopyala.
Diğer komutlar ve Windows/Linux Python yolu `repo/docs/RTX5070_READY.md` içindedir.

## Sohbet ve dosya devamı

Proje devamı bu dosyalara dayanır; sohbetin diğer cihazda görünmesine bağlı
değildir. Yeni sohbet aynı kayıtlı görev noktasını okuyarak devam edebilir.
Konuşma eşitlemesi klasörü başka bilgisayara taşımaz. Resmi açıklama:
[OpenAI Docs — Projects and chats](https://learn.chatgpt.com/docs/projects).

Şu anda Git remote ve bağlı bir RTX5070 yürütücüsü yok; otomatik iki yönlü
eşitleme kurulmuş değil. İleride sık geçiş için özel Git remote üzerinden küçük
kod/rapor/durum dosyaları eşitlenebilir; Git dışındaki büyük checkpoint'ler
ayrıca SHA256 ile taşınır. G0D uzak runner işleri henüz kapalıdır.
İki cihazın aynı görev/durum dosyasını eşzamanlı değiştirmemesi için sırayla
commit ve devir yapılır. Fiziksel olarak diğer cihazda çalışma bu dosya aktarımı
ile sağlanır; hiçbir CUDA hesabı MACM6'da başlatılmaz.
