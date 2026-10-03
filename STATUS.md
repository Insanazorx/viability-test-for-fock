# STATUS — Fock-selected dark-sector programı

Bu görünüm `state/state.yaml` dosyasından üretilir. Güncellemek için `scripts/ctl.py refresh`; elle değiştirilmez.

Durum kaydı (UTC): **2026-10-03T20:41:48.704644+00:00**

## Genel durum

| Başlık | Şu anki durum |
|---|---|
| Bilimsel sonuç | **PARTIAL / UNRESOLVED** |
| Işınımsal değerlendirme | RADIATIVELY_TUNED_EFT; VIABILITY_UNRESOLVED |
| MACM6 | Kayıtlı CPU referans/hazırlıkları tamam; G0 kapsam denetiminde iki RTX-bağımsız yayın benchmark’ı henüz yapılmamış bulundu. |
| Sıradaki tek eylem | G0B-T03 / RTX5070 |
| CLOUD | PAUSED; onaylı gate: yok; çalışma başına USD 0 |
| Yürütme kaydı | 21 görev: 14 PASS, 0 RUNNING, 0 CLAIMED, 7 TODO, 0 FAIL, 0 BLOCKED, 0 ARCHIVED |

**Okuma anahtarı:** `[X]` yalnız ilgili cihazın raporlu sorumluluğunun tamamlandığını, `[ ]` beklediğini, `N/A` o cihazın atanmadığını gösterir. `RUNNING` görev yaşam-durumudur; ertelenmiş bir görevin hesabı şu anda çalışıyor anlamına gelmez.

`PASS · hazırlık` ve `PASS · kısmi kapsam` özgün bilimsel gate’i kapatmaz. `TODO · plan` satırları sözleşmedeki gelecek işlerdir; yürütme kaydına veya çalıştırma kuyruğuna eklenmiş değildir. `Ön koşul bekliyor` ifadesi raporlu `BLOCKED` sonucu değildir.

**Alt gate durumları:** `PASS` tanımlı kapsamın tamamlandığını, `PARTIAL` kısmi ilerlemeyi, `PREPARED` ön hazırlığın yapıldığını, `TODO` işin beklediğini, `DISABLED` isteğe bağlı işin kapalı olduğunu gösterir. Plan satırlarındaki cihaz kutuları gelecekteki sorumluluğu belirtir; CLOUD kutusu bütçe veya çalıştırma onayı değildir.

## Cihazların durumu

| Cihaz | Raporlu tamamlanan sorumluluk | Operasyon durumu |
|---|---|---|
| MACM6 | 14 | Kayıtlı hazırlık tamam; iki RTX-bağımsız G0 benchmark’ı ayrı görev/ayar/rapor bekliyor. |
| RTX5070 | 3 | Kayıtlı görev sırası geçerli. |
| CLOUD | 0 | Kapalı; açık bütçe ve ölçülen kaynak gereği olmadan iş yok. |

Son raporla belgelenmiş tam test paketi: **126 PASS** — [doğrulama raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md>).

## Bütün ana gate’lerin özeti

| Gate | Amaç | Genel sonuç | Alt gate durumu |
|---|---|---|---|
| [G0](#g0) | Tekrar üretim temeli | **PARTIAL** | [G0A](#g0a) PASS, [G0B](#g0b) PARTIAL, [G0C](#g0c) TODO, [G0D](#g0d) DISABLED |
| [G1](#g1) | Sonlu sertlikte tam soliton sektörü | **PARTIAL** | [G1A](#g1a) PREPARED, [G1B](#g1b) TODO, [G1C](#g1c) TODO, [G1D](#g1d) TODO, [G1E](#g1e) TODO, [G1F](#g1f) TODO, [G1G](#g1g) TODO |
| [G2](#g2) | Üretim ve relic abundance | **TODO** | [G2A](#g2a) TODO, [G2B](#g2b) TODO, [G2C](#g2c) TODO, [G2D](#g2d) TODO, [G2E](#g2e) TODO, [G2F](#g2f) TODO |
| [G3](#g3) | Astrofiziksel karanlık | **TODO** | [G3A](#g3a) TODO, [G3B](#g3b) TODO, [G3C](#g3c) TODO, [G3D](#g3d) TODO |
| [G4](#g4) | Doğallık, vakum bozunumu ve kütleçekim | **PARTIAL** | [G4A](#g4a) PASS, [G4B](#g4b) PARTIAL, [G4C](#g4c) PARTIAL, [G4D](#g4d) PREPARED, [G4E](#g4e) TODO |
| [G5](#g5) | Tam Boltzmann kozmolojisi | **TODO** | [G5A](#g5a) TODO, [G5B](#g5b) TODO, [G5C](#g5c) TODO, [G5D](#g5d) TODO, [G5E](#g5e) TODO |
| [G6](#g6) | Likelihood düzeyinde uygulanabilirlik | **TODO** | [G6A](#g6a) TODO, [G6B](#g6b) TODO, [G6C](#g6c) TODO, [G6D](#g6d) TODO, [G6E](#g6e) TODO |

Ana gate kapanışı: **0/7**. Tam kapsamı tamamlanan zorunlu alt gate: **2/35**; ayrıca isteğe bağlı G0D kapalı. Görev sayıları veya hazırlıklar bilimsel ilerleme yüzdesi olarak kullanılmaz.

Kapsam: **36 alt gate**, AGENTS.md’de açıkça numaralandırılmış **68 görev**, ayrıca raporlu hazırlık/kısmi kapsam kayıtları. T-ID tanımlanmayan gate’ler tam kapsam satırıyla görünür; yeni görev ID’si uydurulmaz.

## Bağımlılık haritası

```text
G0A → G0B → G0C → G0D (isteğe bağlı)
G0B → G1A → G1B → G1C → G1D
                 └→ G1E → G1F → G1G
G1B + G1E → G2A → G2B → G2C → G2D → G2E → G2F
G1G + G2F → G3A → G3B → G3C → G3D
G0A → G4A → G4B → G4C → G4E
G1B → G4D; G1B ölçümleri → G4E kompaktlık
G2F + G3D + G4C + G4D → G5A → G5B → G5C → G5D → G5E
G5E → G6A → G6B → G6C → G6D → G6E
```

G4 teori hattı erken ve paralel ilerleyebilir. Hazırlık görevleri bu bilimsel bağımlılıkları kaldırmaz. Bulut gerekliliği ve bütçesi ayrı kontrol edilir.

<a id="g0"></a>
## G0 — Tekrar üretim temeli

<a id="g0a"></a>
### G0A — Repo, ortam ve kontrol düzlemi

**Durum:** PASS · **Ön koşul:** Başlangıç · **Cihaz sırası:** MACM6 → RTX5070 çekirdek doğrulaması

Kod, matematik çekirdeği ve kayıt disiplinini doğrulamak.

**Kapanış ölçütü:** Gerekli çekirdek cihazları ve kayıt altyapısı kendi raporlarıyla PASS.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G0A-T01 | **Repo iskeleti** — Dizinler, Git dışlama kuralları, bağımlılıklar, şema, durum dosyası ve rapor şablonu kayıtlı. | PASS | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T01__G0A-T01__MACM6__20261001T042108Z__c131218__3e5f3754__REPORT.md>); Repo ve kontrol dosyaları kayıtlı. |
| G0A-T02 | **Matematik çekirdeği API** — C1/C2, Hodge ayrışımı, STF, indirgenmiş alan/enerji/Hopf tanımları; float64 kimlik, dönüşüm ve türev kontrolleri; CUDA aynası. | PASS | [X] | [X] | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T02__G0A-T02__MACM6__20261001T060259Z__ec15d04__1f458c06__REPORT.md>), [RTX5070 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T02__G0A-T02__RTX5070__20261003T203001Z__c8536f6__af3d0bec__REPORT.md>); MACM6 PASS; CUDA aynası henüz çalıştırılmadı. |
| G0A-T03 | **Çalışma ve ayar disiplini** — Sabit ayar kimliği, UTC/Git/config çalışma kimliği, değişmez metadata ve açık kirli Git bilgisi. | PASS | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T03__G0A-T03__MACM6__20261001T174323Z__9336699__a64a600a__REPORT.md>); MACM6 ortamı/ayar/çalışma kaydı tamamlandı. |
| G0A-T04 | **MACM6 tamamlama ve aktarım hazırlığı** — Önceki 13 MACM6 sorumluluğunun rapor/ayar/bütünlük denetimi ve offline aktarım ön kontrolü PASS. | PASS · hazırlık | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T04__G0A-T04__MACM6__20261003T104642Z__ff719b7__32d67550__REPORT.md>); Bu hazırlıkla toplam 14 MACM6 sorumluluğu raporlu; ZIP geri yükleme doğrulaması aktarım kaydında. |

<a id="g0b"></a>
### G0B — Yayınlanan indirgenmiş Hopf çözücüsü

**Durum:** PARTIAL · **Ön koşul:** G0A · **Cihaz sırası:** MACM6 referans → RTX5070 üretim → MACM6 analiz

Makaledeki durağan alan ve fiziksel Hessian sonuçlarını yeniden üretmek.

**Kapanış ölçütü:** Durağan 17³/21³/25³/33³ dizisi, yük ve fiziksel spektrum yayınlanan hedefleri sağlamalı.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G0B-T01 | **Statik enerji ve spektral türevler** — Eq.65 enerjisi; analitik periyodik alan türev yakınsaması, Parseval ve vakum sınırı kontrolleri. | PASS | [X] | [X] | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T01__G0B-T01__MACM6__20261001T183741Z__5e9474e__8baddf31__REPORT.md>), [RTX5070 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T01__G0B-T01__RTX5070__20261003T203207Z__a12ca3e__9e664616__REPORT.md>); MACM6 enerji ve türev referansı PASS; CUDA karşılaştırması bekliyor. |
| G0B-T02 | **Hopf yükü ve işaret** — Coulomb-gauge FFT ters çözümü; birim alan Q≈−1, düzgün deformasyon ve trivial alan kontrolü. | PASS | [X] | [X] | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md>), [RTX5070 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md>); MACM6 yük/işaret/deformasyon kontrolü PASS; CUDA bekliyor. Checkpoint durağan değil. |
| G0B-T03 | **Augmented-Lagrangian minimizasyonu** — 17³/21³/25³/33³; artık toleransı, sonlu değerler; bağıl enerji farkı≤5e−4, \|\|Q\|−1\|≤5e−4; virial eğilimi. | TODO | [ ] | [ ] | N/A | Rapor yok; G0B-T05 hazırlığı PASS; yayınlanan durağan GPU dizisi ve MACM6 fit raporu yapılmadı. |
| G0B-T04 | **İndirgenmiş fiziksel Hessian** — Teğet/yük izdüşümü, matris kurmadan HVP, kolektif modlar; HVP/simetri/özçift artığı ve pozitif ilk fiziksel aralık. | TODO | [ ] | [ ] | N/A | Rapor yok; G0B-T05 HVP hazırlığı PASS; kolektif katalog/eigensolver ve fiziksel spektrum üretilmedi. |
| G0B-T05 | **MACM6 indirgenmiş çözücü/HVP/CPU oracle hazırlığı** — G0B-T03/T04 ve G0C girdileri için hazırlık; durağan soliton/fiziksel spektrum kabulü değil. | PASS · hazırlık | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md>); G0B-T03/T04 ve G0C girdileri için hazırlık; durağan soliton/fiziksel spektrum kabulü değil. |

<a id="g0c"></a>
### G0C — Cihazlar arası referans ve hassasiyet

**Durum:** TODO · **Ön koşul:** G0B · **Cihaz sırası:** MACM6 ↔ RTX5070

CPU/CUDA farklarının ve düşük özdeğer işaretlerinin güvenilirliğini ölçmek.

**Kapanış ölçütü:** Enerji, yük, gradyan ve HVP farkları açıklanmalı; belirsiz özdeğer PASS olmaz.

**Koşullu kaynak:** Yalnız ölçülen hassasiyet yetersizliği varsa ve onayla CLOUD FP64.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G0C-T01 | **Bağımsız CPU/CUDA karşılaştırması** — Basit float64 CPU referansı ile enerji, Q, gradyan ve yönsel HVP karşılaştırması. | TODO | [ ] | [ ] | N/A | Rapor yok; G0B-T05 doğrudan DFT CPU oracle hazır; gerçek CUDA karşılaştırması henüz yok. |
| G0C-T02 | **Hassasiyet politikası** — RTX5070 float32/float64/seçilen karma hassasiyet profili; son gözlenebilirlerin ve sıfıra yakın özdeğerlerin yeniden doğrulanması. | TODO | [ ] | [ ] | N/A | Rapor yok; RTX hassasiyet profili olmadan MACM6 hata bütçesi tamamlanamaz. |

<a id="g0d"></a>
### G0D — İsteğe bağlı uzak/telefon kontrolü

**Durum:** DISABLED · **Ön koşul:** G0B, G0C · **Cihaz sırası:** MACM6 → RTX5070

Onaylı görevlerle sınırlı denetlenebilir uzak çalıştırma.

**Kapanış ölçütü:** G0B PASS öncesinde etkinleştirilmez; bulut sağlama yok.

**Kapsam notu:** Opsiyonel; mevcut görevlerin enabled=false durumu korunuyor.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G0D-T01 | **MACM6 self-hosted runner** — macm6 etiketi; yalnız onaylı script/ayarlar; güvenilmeyen PR üzerinden keyfi komut yok. | TODO · kapalı | [ ] | N/A | N/A | Rapor yok |
| G0D-T02 | **RTX5070 self-hosted runner** — rtx5070 etiketi; gerçek CUDA görünürlüğü; aynı anda tek GPU işi. | TODO · kapalı | N/A | [ ] | N/A | Rapor yok |
| G0D-T03 | **Telefon workflow dispatch** — status/run-task/pause/cancel/collect-report; keyfi kabuk veya bulut başlatma yok. | TODO · kapalı | [ ] | [ ] | N/A | Rapor yok |


<a id="g1"></a>
## G1 — Sonlu sertlikte tam soliton sektörü

<a id="g1a"></a>
### G1A — Altı bileşenli tam statik teori

**Durum:** PREPARED · **Ön koşul:** G0B · **Cihaz sırası:** MACM6 matematik/referans → RTX5070 uygulama

Sabit yarıçap/Pfaffian indirgemesini kaldırmak.

**Kapanış ölçütü:** Tam M enerjisi ve türevleri, ağır normal mod limiti ve gerçek checkpoint kaldırma doğrulanmalı.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1A-T01 | **Altı bileşenli alan ve tam enerji** — C1/C2/M±, radyal/Pfaffian potansiyelleri, tam quartic operatör; SO4, indirgenme ve sonlu fark türevleri. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor; G1A-T04 CPU tam alan/türev hazırlığı PASS; özgün görevin üretim/CUDA kabulü bekliyor. |
| G1A-T02 | **Durağan Hopf alanını tam M alanına kaldırma** — Yeniden üretilmiş durağan checkpoint; C1−σ0², C2, Q±; ağır normal mod limitinde indirgenmiş enerji. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor; Bağımsız başlangıç alanı var; yeniden üretilmiş durağan checkpoint yok. |
| G1A-T03 | **Sertlik devam parametreleri** — A=αζ/ZM², P=μζ/ZM²; logaritmik/adaptif adımlar ve önceki çözümle başlangıç. | TODO · plan | N/A | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1A-T04 | **MACM6 tam M enerji ve türev referansı** — Tam gradyan/HVP/SO4/ağır limit kontrolü; özgün G1A üretim görevleri açık. | PASS · hazırlık | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G1\G1A-T04__G1A-T04__MACM6__20261003T102101Z__5f01a82__771488e7__REPORT.md>); Tam gradyan/HVP/SO4/ağır limit kontrolü; özgün G1A üretim görevleri açık. |

<a id="g1b"></a>
### G1B — Dal varlığı, çözünürlük ve kutu yakınsaması

**Durum:** TODO · **Ön koşul:** G1A · **Cihaz sırası:** RTX5070 → MACM6 yakınsama analizi

Sonlu sertlikte çözülmüş, lokalize ve devam edebilir bir soliton dalı bulmak.

**Kapanış ölçütü:** Son iki güvenilir çözünürlükte E/RH farkı<%1; yük, artık ve hacim etkileri yakınsamış.

**Koşullu kaynak:** T05 sonrası belirli yüksek çözünürlük/FP64 doğrulaması için CLOUD; şu anda onay yok.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1B-T01 | **İlk tam M durağan noktası** — Önce 33³; E/RH/Q±, artıklar, radyal ve C2 deformasyonu, minimum sektör normu; çözülmüş lokalize çekirdek. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1B-T02 | **Sertlik devam haritası** — A/P dal takibi; bifurkasyonda adım azaltma; dal kaybı veya çözülmeyen çekirdekte durma. | TODO · plan | N/A | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1B-T03 | **Çözünürlük dizisi** — 33³/49³/65³, gerekirse97³; önce ölçülen VRAM; E/RH ve topoloji/artık yakınsaması. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1B-T04 | **Kutu boyutu dizisi** — Sabit çözülmüş aralıkta kutu büyütme; E/RH/virial/şekil değişimi önemsiz olmalı. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1B-T05 | **Buluta yükseltme kararı** — T01–T04 PASS, açık bir kalan soru ve RTX bellek/süre profili; onaylı sınırlı doğrulama. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g1c"></a>
### G1C — Tam fiziksel Hessian

**Durum:** TODO · **Ön koşul:** G1B · **Cihaz sırası:** RTX5070 pilot → MACM6 mod kataloğu/analiz

Sonlu sertlikte gerçek negatif fiziksel mod bulunup bulunmadığını belirlemek.

**Kapanış ölçütü:** Yakınsamış tam teoride sağlam negatif fiziksel mod olmamalı; hassasiyete duyarlı işaret açık kalır.

**Koşullu kaynak:** T03 işareti/boyutu gerektirirse onaylı CLOUD FP64.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1C-T01 | **Tam matris kurmadan HVP** — Yönsel sonlu fark ve çift doğrusal simetri kontrolü; yoğun kafes Hessianı yok. | TODO · plan | N/A | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor; G1A-T04 CPU analitik HVP hazırlığı var; durağan tam teori CUDA HVP görevi yapılmadı. |
| G1C-T02 | **Kolektif mod kataloğu** — Yalnız gerekçeli öteleme/dönme/iç dönme/projektör sıfırlarını ayır; şüpheli küçük modları keyfi silme. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1C-T03 | **En düşük fiziksel spektrum** — Birden fazla çözünürlükte özçiftler; işaret ve artık kontrolü; negatif mod bilimsel durdurma gerekçesi. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1C-T04 | **λ yanıtı ve skaler yük** — Yakın λ çözümlerinden βH=MPl∂λlnMH; hatalı sabit örnek değer kullanma. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g1d"></a>
### G1D — En düşük enerjili çözülme eyeri

**Durum:** TODO · **Ön koşul:** G1C · **Cihaz sırası:** RTX5070 NEB pilot → MACM6 yol denetimi

Hopfiondan vakuma çözülme bariyerini bulmak.

**Kapanış ölçütü:** ΔEunwind>0 ve çözünürlük kararlı; statik bariyer tek başına kozmolojik ömür değildir.

**Koşullu kaynak:** Yalnız nihai yüksek çözünürlüklü eyer inceltmesi için CLOUD.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1D-T01 | **Başlangıç yolunun kurulması** — Sonlu sertlik Hopfion/vakum uçları; radyal ve Pfaffian yönlerinden geçişe izin ver. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1D-T02 | **NEB/string yöntemi** — Önce az sayıda görüntü; dik kuvvet, görüntü aralığı, enerji ve topoloji boyunca tanılama. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1D-T03 | **Eyer inceltme** — En yüksek enerji görüntüsünü eyer aramasıyla iyileştir; ΔEunwind(A,P) ve yakınsama. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g1e"></a>
### G1E — Gerçek zaman kararlılığı ve hiperboliklik

**Durum:** TODO · **Ön koşul:** G1B · **Cihaz sırası:** MACM6 türetim → RTX5070 dinamik → MACM6 denetim

Evrimin güçlü gradyanlarda da geçerli PDE bölgesinde kaldığını ölçmek.

**Kapanış ölçütü:** Enerji/yük sapmaları kontrollü; prensipal sembolde kinetik/gradyan işaret kaybı veya karmaşık hız yok.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1E-T01 | **Tam PDE formülasyonu** — EFT kaynaklı method-of-lines denklemleri; prensipal katsayıların bağımsız MACM6 kontrolü. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1E-T02 | **Şeffaf zaman integratörü** — Önce RK4/CFL; serbest dalga, Hessian frekansları ve kapalı kutu enerji sapması kontrolleri. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1E-T03 | **Pertürbe soliton ömrü** — Rastgele ve moda hizalı bozunum; enerji/yük/çekirdek, radyasyon ve C1/C2 kaydı. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1E-T04 | **Hiperboliklik izleyicisi** — Kaydedilen her zamanda prensipal sembol; minimum kinetik/gradyan özdeğerleri ve karakteristik hızlar. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g1f"></a>
### G1F — Çarpışma pilotları

**Durum:** TODO · **Ön koşul:** G1E · **Cihaz sırası:** RTX5070 pilot → MACM6 analiz

Doğrulanmış başlangıç ve sınır koşullarıyla temsilî kanalları çözmek.

**Kapanış ölçütü:** Sınır yansıması ve enerji/yük tanıları kontrollü; çarpışma boyunca hiperboliklik korunmuş.

**Kapsam notu:** Pilotlar kararlı olmadan CLOUD yok.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1F-T01 | **Boost edilmiş iki soliton** — Hız, etki parametresi, yük eşleşmesi ve iç yönelim açıkça tanımlı/doğrulanmış. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1F-T02 | **Sınır koşulları** — Yeterli kutu ve test edilmiş sünger/absorban alan; serbest dalgayla yansıma ölçümü. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1F-T03 | **Temsilî kanallar** — Aynı/zıt yük ve karışık sektör; birden fazla iç yönelim. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1F-T04 | **Çarpışma tanıları** — Q±(t), çekirdek sayısı, çıkan hız/açı, dalga enerjisi, yakalama/yok olma/yük aktarımı ve hiperboliklik. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g1g"></a>
### G1G — Çarpışma kampanyası ve kesitler

**Durum:** TODO · **Ön koşul:** G1F · **Cihaz sırası:** RTX5070 küçük kampanya → MACM6 tasarım → CLOUD topluluk → MACM6 indirgeme

Mikroskopik etkileşim çekirdeklerini belirsizlikleriyle üretmek.

**Kapanış ölçütü:** Kesit/kanal tabloları, seçilmiş sürekli limit kontrolleri ve üretim aktarımı mevcut.

**Koşullu kaynak:** CLOUD topluluk işi ancak pilot PASS, kaynak profili ve açık bütçeyle.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G1G-T01 | **Adaptif örnekleme tasarımı** — Hız/etki/yönelim/sertlik; yalnız kanal sınırları ve rezonanslarda sıklaştırma. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1G-T02 | **Mikroskopik kesitler** — Transfer, yok olma, yakalama, yük değişimi ve radyasyon payı belirsizlikleri. | TODO · plan | [ ] | [ ] | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1G-T03 | **Çarpışma yakınsaması** — Temsilî sınıfları daha yüksek çözünürlükte yeniden doğrula. | TODO · plan | [ ] | [ ] | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G1G-T04 | **Üretim aktarımı** — Gate2/3 için sürümlenmiş çarpışma çekirdek tabloları ve belirsizlikleri. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |


<a id="g2"></a>
## G2 — Üretim ve relic abundance

<a id="g2a"></a>
### G2A — Kapalı FLRW ve enerji muhasebesi

**Durum:** TODO · **Ön koşul:** G1B, G1E · **Cihaz sırası:** MACM6 türetim/referans → RTX5070 smoke

Elle verilmiş bath yerine EFT toplam korunumunu uygulamak.

**Kapanış ölçütü:** Kapalı ODE, Friedmann kısıtı ve sektörler arası enerji alışveriş artığı kontrollü.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G2A-T01 | **Kapalı enerji alışverişi** — Madde/karanlık sektör, M/χ/λ gerilmeleri ve ölçek faktörünü birlikte muhasebeleştir. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2A-T02 | **Kapalı homojen benchmark** — 3B öncesinde ODE tetikleme, toplam Friedmann ve alışveriş artık kontrolü. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2A-T03 | **Komoving alan denklemleri** — Sertliği azaltan açık değişken seçimi ve bağımsız formül kontrolü. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g2b"></a>
### G2B — Genişleyen kafes pilotu

**Durum:** TODO · **Ön koşul:** G2A · **Cihaz sırası:** MACM6 ayar kontrolü → RTX5070

M/χ/λ için doğrulanmış komoving 3B üretim kodunu ölçmek.

**Kapanış ölçütü:** 64³ PASS sonra96³/128³; enerji/Friedmann artığı, topoloji, VRAM ve hız ölçülmüş.

**Kapsam notu:** Bu aşamada CLOUD yasak.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G2B-T01 | **3B komoving çözücü** — Altı M, χ, λ; viability koşusu G2A kapalı enerji muhasebesini kullanır. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2B-T02 | **Başlangıç dalgalanmaları** — Dağılım, genlik, UV kesimi, seed ve normalizasyon sabit/verilmiş. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2B-T03 | **64³ pilot** — Kararlılık, korunum artığı, topoloji oluşumu, VRAM ve throughput. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2B-T04 | **96³/128³ pilot** — Yalnız64³ PASS ve ölçülen bellek bütçesinden sonra. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g2c"></a>
### G2C — Soliton bulucu ve izleyici

**Durum:** TODO · **Ön koşul:** G2B · **Cihaz sırası:** MACM6 prototip → RTX5070 gerçek snapshot

Dalga/noise içinde gerçek nesneleri tespit ve takip etmek.

**Kapanış ölçütü:** Yalıtılmış/boost/iki-soliton/noise doğrulamasında yanlış pozitif/negatif oranları raporlu.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G2C-T01 | **Aday çekirdek tespiti** — Enerji ve çekirdek tanılarından aday lokal nesneleri öner. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2C-T02 | **Topolojik yük doğrulaması** — Dalga arka planına dayanıklı yerel/global topoloji tanıları. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2C-T03 | **Zaman boyunca takip** — Konum, hız, yük, birleşme/yok olma geçmişi. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2C-T04 | **Sentetik doğrulama** — Yalıtılmış, boost edilmiş, iki-soliton ve saf dalga/noise; hata oranları. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g2d"></a>
### G2D — Kaba üretim parametre haritası

**Durum:** TODO · **Ön koşul:** G2C · **Cihaz sırası:** MACM6 tasarım → RTX5070 tarama → MACM6 sınıflandırma

Verimli taramayla umut veren açık bölgeleri seçmek.

**Kapanış ölçütü:** Birden fazla seed ve otomatik erken red; rastgele tek başarılı nokta yeterli değil.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G2D-T01 | **Boyutsuz parametre indirgeme** — Taramadan önce gereksiz ölçekleri kaldır. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2D-T02 | **Verimli kaba tasarım** — Sobol/Latin-hypercube veya eşdeğeri; kör yoğun çok boyutlu ızgara yok. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2D-T03 | **Çok seed pilotu** — Umut veren her nokta birkaç seed ile doğrulanmış. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2D-T04 | **Erken red** — Soliton yokluğu, hiperboliklik kaybı, aşırı dalga, enerji bütçesi veya yanlış bolluk eğilimi reddedilir. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g2e"></a>
### G2E — Üretim yakınsaması, hacim ve topluluk

**Durum:** TODO · **Ön koşul:** G2D · **Cihaz sırası:** RTX5070 doğrulama → MACM6 bulut paketi → CLOUD → MACM6

Açık parametre bölgesinde gerçek relic abundance üretimini doğrulamak.

**Kapanış ölçütü:** Bolluk ve tam enerji redshift muhasebesi açık bir bölgede kabul edilebilir; seed/hacim/çözünürlük belirsizliği kontrolü.

**Koşullu kaynak:** CLOUD için sabit ayar, ölçülen kaynak gereği, tahmin ve açık bütçe şart.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G2E-T01 | **Umut veren açık bölgeler** — Buluta yalnız çok-seed pilotta sağlam bölgeler; tek şanslı nokta yok. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2E-T02 | **Çözünürlük ölçekleme** — Doğrulanmış RTX grid →256³;384³/512³ ancak yakınsama gerektirirse. | TODO · plan | [ ] | [ ] | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2E-T03 | **Hacim ölçekleme** — Kafes aralığı ve sonlu hacim istatistiğini ayır. | TODO · plan | [ ] | [ ] | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2E-T04 | **Seed topluluğu** — Sayı yoğunluğu, yük dağılımı, korelasyon uzunluğu ve dalga payı varyansı. | TODO · plan | [ ] | [ ] | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G2E-T05 | **Relic abundance** — Tam enerji bütçesini tutarlı redshift ile bugüne taşı; elle tek nokta normalizasyonu yok. | TODO · plan | [ ] | [ ] | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g2f"></a>
### G2F — Üretimden kinetik ve kapanış verileri

**Durum:** TODO · **Ön koşul:** G2E, G1C · **Cihaz sırası:** MACM6 analiz + seçilmiş RTX5070 işleme

Örnek closure katsayılarını ölçülen dağılımlarla değiştirmek.

**Kapanış ölçütü:** nH(a), kütle/hız dağılımı, dalga/shot-noise/isocurvature, ses hızı, boyut/anisotropic stress ve βH belirsizlikli tabloları.

**Koşullu kaynak:** Yalnız büyük ham verinin bulunduğu bulut depolama yakınlığı gerektirirse CLOUD indirgeme.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G2F | **Tam gate kapsamı** — nH(a), kütle/hız dağılımı, dalga/shot-noise/isocurvature, ses hızı, boyut/anisotropic stress ve βH belirsizlikli tabloları. | TODO · plan | [ ] | [ ] | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |


<a id="g3"></a>
## G3 — Astrofiziksel karanlık

<a id="g3a"></a>
### G3A — Öz etkileşim ve sayı değiştiren oranlar

**Durum:** TODO · **Ön koşul:** G1G, G2F · **Cihaz sırası:** MACM6; yalnız eksik çarpışma noktaları için RTX5070

Ölçülen çarpışmaları fiziksel birimlere çevirmek.

**Kapanış ölçütü:** σT(v)/MH ve üretilen hız dağılımında yok olma/yakalama/yük değişimi oranları belirsizlikli.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G3A-T01 | **Fiziksel birimlere dönüşüm** — G1G boyutsuz kesitleri korunmuş her fiziksel ölçek seçimine dönüştür. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G3A-T02 | **Transfer kesiti** — σT(v)/MH tablosu ve interpolasyon belirsizliği. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G3A-T03 | **Sayı değiştiren oranlar** — Üretilen hız dağılımından yok olma/yakalama/yük değişimi. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g3b"></a>
### G3B — Skaler ve uzun menzilli kuvvetler

**Durum:** TODO · **Ön koşul:** G3A, G1C · **Cihaz sırası:** MACM6

Ölçülen skaler yükün astrofiziksel etkisini sınamak.

**Kapanış ölçütü:** Ölçülen βH ile menzil/çevre, beşinci kuvvet ve artık teğet mod etkileri; örnek βH=0.02 yerine gerçek veri.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G3B | **Tam gate kapsamı** — Ölçülen βH ile menzil/çevre, beşinci kuvvet ve artık teğet mod etkileri; örnek βH=0.02 yerine gerçek veri. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g3c"></a>
### G3C — Görünür sektör ve yıldız sınırları

**Durum:** TODO · **Ön koşul:** G3B · **Cihaz sırası:** MACM6

Portalın gözlem ve yıldız fiziğiyle uyumunu denetlemek.

**Kapanış ölçütü:** Veri sürümleri/kaynakları sabit; saçılma, eşdeğerlik/beşinci kuvvet, soğuma, yakalama/ısıtma ve yapı sınırları.

**Koşullu kaynak:** Yalnız ölçülen entegrasyon maliyeti gerektirirse CLOUD CPU.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G3C | **Tam gate kapsamı** — Veri sürümleri/kaynakları sabit; saçılma, eşdeğerlik/beşinci kuvvet, soğuma, yakalama/ısıtma ve yapı sınırları. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g3d"></a>
### G3D — Astrofiziksel izinli bölge

**Durum:** TODO · **Ön koşul:** G3C · **Cihaz sırası:** MACM6

Gate1/2/3 koşullarının ortak açık bölgesini bulmak.

**Kapanış ölçütü:** Belirsizliklerden sonra sonlu/açık izinli bölge ve makine tarafından okunabilir tablo mevcut.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G3D | **Tam gate kapsamı** — Belirsizliklerden sonra sonlu/açık izinli bölge ve makine tarafından okunabilir tablo mevcut. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |


<a id="g4"></a>
## G4 — Doğallık, vakum bozunumu ve kütleçekim

<a id="g4a"></a>
### G4A — Operatör ve simetri denetimi

**Durum:** PASS · **Ön koşul:** G0A · **Cihaz sırası:** MACM6

Seçilen EFT mertebesinde korunmuş ve ayarlanmış yapıları ayırmak.

**Kapanış ölçütü:** Seçilen d≤4/IBP karanlık+metrik kapsamındaki üç denetim PASS; belirtilmeyen madde modeli kapsam dışında.

**Kapsam notu:** PASS yalnız seçilen operatör kapsamı için; bütün G4 veya doğalılık kararı kapanmış değildir.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G4A-T01 | **Seçilen mertebede operatör bazı** — Diffeomorfizm, SO4, χ-paritesi; seçilen mertebede envanter ve kapsam kaydı. | PASS | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4A-T01__G4A-T01__MACM6__20261001T193427Z__8e637b1__f5f125f4__REPORT.md>) |
| G4A-T02 | **Eksik operatör ve redundant terimler** — Simetri, ek baseline yansıma ve koşullu field/EOM değişimi ile ayar farkları. | PASS | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4A-T02__G4A-T02__MACM6__20261003T102719Z__48b2e46__59ca8890__REPORT.md>) |
| G4A-T03 | **μ ve Xi fonksiyon denetimi** — λⁿC2² alt terimleri ve Xi parite/doyum biçimi; matching koşulları açık. | PASS | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4A-T03__G4A-T03__MACM6__20261003T102746Z__d2910a1__08b1fafb__REPORT.md>) |

<a id="g4b"></a>
### G4B — Tek döngü EFT düzeltmeleri ve eşleşme

**Durum:** PARTIAL · **Ön koşul:** G4A · **Cihaz sırası:** MACM6

Skaler kütle/vakum enerjisi/switching/mixing/portal düzeltmelerini eşlemek.

**Kapanış ölçütü:** Karanlık sektörün yanında somut madde/portal, kinetik/eğrilik, renormalizasyon, fiziksel tuning ve cutoff eşleşmesi tamamlanmış.

**Kapsam notu:** G4B-T01 yalnız homojen karanlık-skaler hesabının PASS raporudur; tam G4B kapsamı henüz açık.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G4B | **Tam gate kapsamı** — Karanlık sektörün yanında somut madde/portal, kinetik/eğrilik, renormalizasyon, fiziksel tuning ve cutoff eşleşmesi tamamlanmış. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G4B-T01 | **Homojen karanlık-skaler tek döngü hesabı** — Homojen karanlık sektör determinantı/UV pole/ölçek/mixing kontrolü; portal ve tam matching açık. | PASS · kısmi kapsam | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4B-T01__G4B-T01__MACM6__20261003T103247Z__d64b18b__39461767__REPORT.md>); Homojen karanlık sektör determinantı/UV pole/ölçek/mixing kontrolü; portal ve tam matching açık. |

<a id="g4c"></a>
### G4C — Tam doğalılık karar dalı

**Durum:** PARTIAL · **Ön koşul:** G4B · **Cihaz sırası:** MACM6

Dört seçenekten birini tam hesabın kapsamıyla seçmek.

**Kapanış ölçütü:** Teknik doğal / uygun ama ayarlı / ek koruma gerekir / kontrolsüz ayrımı tam girdilerle yapılmış; ek koruma seçilirse yeni teori dalı.

**Kapsam notu:** G4C-T02 koşullu hazırlık: RADIATIVELY_TUNED_EFT; VIABILITY_UNRESOLVED. Uygunluk nitelemesi henüz verilmedi.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G4C | **Tam gate kapsamı** — Teknik doğal / uygun ama ayarlı / ek koruma gerekir / kontrolsüz ayrımı tam girdilerle yapılmış; ek koruma seçilirse yeni teori dalı. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |
| G4C-T02 | **Koşullu doğalılık değerlendirmesi** — Işınımsal ayar gereği kaydedildi; tam bilimsel uygunluk kararı verilmedi. | PASS · hazırlık | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4C-T02__G4C-T02__MACM6__20261003T103849Z__bcf5cc8__dda1cf83__REPORT.md>); Işınımsal ayar gereği kaydedildi; tam bilimsel uygunluk kararı verilmedi. |

<a id="g4d"></a>
### G4D — Yerçekimli vakum bozunumu

**Durum:** PREPARED · **Ön koşul:** G1B · **Cihaz sırası:** MACM6

CDL geri tepkisi ve prefaktörle kozmolojik ömür bölgesini bulmak.

**Kapanış ölçütü:** Korunmuş parametre bölgesinde yerçekimli eylem ve haklı düzeyde prefaktör; gereken kozmolojik süreden uzun ömür.

**Kapsam notu:** G4D-T04 düz uzay regresyonunu ve denklem/vakum geometri hazırlığını geçti. G4D-T01..T03 özgün görev kutuları/ön koşulları kapanmadı.

**Koşullu kaynak:** Yalnız geniş ve ölçülmüş maliyetli tarama için CLOUD CPU.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G4D-T01 | **Düz uzay bounce tekrar üretimi** — Yayınlanan Bhat4 katsayısı, başlangıç, virial ve truncation/yakınsama denetimi. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor; G4D-T04 içinde katsayı tekrar üretildi; bu özgün görev yeniden açılmadı/aktarılmadı ve G1B ön koşulu duruyor. |
| G4D-T02 | **Yerçekimli CDL çözümü** — O4 bounce ve Einstein geri tepkisi; iki düzenli kutup, kısıt ve false-vacuum eylem çıkarımı. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor; G4D-T04 kısıt ve sabit vakum testleri geçti; nontrivial yerçekimli bounce çözülmedi. |
| G4D-T03 | **Fiziksel ömür bölgesi** — Ölçekler ve prefaktörün EFT kontrolü; korunmuş bölgede kozmolojik ömür. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor; Fiziksel ölçek, korunmuş bölge, CDL çözümü ve prefaktör bekliyor. |
| G4D-T04 | **Düz uzay bounce ve CDL denklem hazırlığı** — Kaynak bounce tekrar üretimi/kısıt/sabit vakum kontrolü; fiziksel CDL ömrü değil. | PASS · hazırlık | [X] | N/A | N/A | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4D-T04__G4D-T04__MACM6__20261003T103854Z__ffaee76__f64c5f3a__REPORT.md>); Kaynak bounce tekrar üretimi/kısıt/sabit vakum kontrolü; fiziksel CDL ömrü değil. |

<a id="g4e"></a>
### G4E — Solitonda kütleçekim önem testi

**Durum:** TODO · **Ön koşul:** G4C, G1B · **Cihaz sırası:** MACM6 tahmin; yalnız gerekirse RTX5070/CLOUD

Önce kompaktlıkla daha pahalı GR hesabının gereğini belirlemek.

**Kapanış ölçütü:** GMH/RH≪1 ise sayısal ihmal kanıtı; değilse birleşik gravitating çözüm ve ilgili kararlılık tekrarı.

**Koşullu kaynak:** Ölçülen kompaktlık gerektirirse RTX5070/CLOUD; otomatik GR kampanyası yok.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G4E | **Tam gate kapsamı** — GMH/RH≪1 ise sayısal ihmal kanıtı; değilse birleşik gravitating çözüm ve ilgili kararlılık tekrarı. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |


<a id="g5"></a>
## G5 — Tam Boltzmann kozmolojisi

<a id="g5a"></a>
### G5A — Tür modeli ve başlangıç koşulları

**Durum:** TODO · **Ön koşul:** G2F, G3D, G4C, G4D · **Cihaz sırası:** MACM6

Üretim verilerine dayalı tam lineer sistemi kurmak.

**Kapanış ölçütü:** Hopf yoğunluk/hız/ses/gerilme, dalgalar, χ/λ, noise/isocurvature, radyasyon/nötrino/metrik ve süper-horizon başlangıcı.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G5A | **Tam gate kapsamı** — Hopf yoğunluk/hız/ses/gerilme, dalgalar, χ/λ, noise/isocurvature, radyasyon/nötrino/metrik ve süper-horizon başlangıcı. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g5b"></a>
### G5B — CLASS uygulaması

**Durum:** TODO · **Ön koşul:** G5A · **Cihaz sırası:** MACM6

Minimum müdahaleyle doğrulanabilir Boltzmann uzantısı.

**Kapanış ölçütü:** Temiz ayrışma limiti; açık parametreler; sabit üretim değerleri yok; sürümlü G2F tablosu girişi.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G5B | **Tam gate kapsamı** — Temiz ayrışma limiti; açık parametreler; sabit üretim değerleri yok; sürümlü G2F tablosu girişi. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g5c"></a>
### G5C — Kozmolojik kararlılık ve regresyon

**Durum:** TODO · **Ön koşul:** G5B · **Cihaz sırası:** MACM6

Tam sistemin ayrışma ve korunum limitlerini denetlemek.

**Kapanış ölçütü:** βH→0, dalga→0, soğuk limit, gauge/regresyon, ghost/gradyan yokluğu, süper-horizon ve korunum kontrolleri.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G5C | **Tam gate kapsamı** — βH→0, dalga→0, soğuk limit, gauge/regresyon, ghost/gradyan yokluğu, süper-horizon ve korunum kontrolleri. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g5d"></a>
### G5D — Spektrum üretimi

**Durum:** TODO · **Ön koşul:** G5C · **Cihaz sırası:** MACM6 geliştirme

Denetlenmiş modelden kozmolojik gözlenebilirleri çıkarmak.

**Kapanış ölçütü:** CMB TT/TE/EE, lensing, P(k), büyüme, transfer/isocurvature; ucuz erken hata tanıları.

**Koşullu kaynak:** Topluluk üretimi için gerekçeli/onaylı CLOUD CPU.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G5D | **Tam gate kapsamı** — CMB TT/TE/EE, lensing, P(k), büyüme, transfer/isocurvature; ucuz erken hata tanıları. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g5e"></a>
### G5E — Emülatör gereklilik kararı

**Durum:** TODO · **Ön koşul:** G5D · **Cihaz sırası:** MACM6 karar

Likelihood darboğazı ölçülmeden surrogate geliştirmemek.

**Kapanış ölçütü:** Profil CLASS süresini darboğaz gösterirse held-out doğrulamalı sınırlı alan emülatörü; aksi halde gerek yok raporu.

**Koşullu kaynak:** Profil ve bütçeyle CLOUD CPU/GPU; emülatör isteğe bağlı.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G5E | **Tam gate kapsamı** — Profil CLASS süresini darboğaz gösterirse held-out doğrulamalı sınırlı alan emülatörü; aksi halde gerek yok raporu. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |


<a id="g6"></a>
## G6 — Likelihood düzeyinde uygulanabilirlik

<a id="g6a"></a>
### G6A — Likelihood altyapısı ve veri dondurma

**Durum:** TODO · **Ön koşul:** G5E · **Cihaz sırası:** MACM6

Tek inference çatısı ve aşamalı veri sözleşmesi seçmek.

**Kapanış ölçütü:** Cobaya veya MontePython seçimi; veri/nuisance/prior/covariance/likelihood sürümleri sabit.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G6A | **Tam gate kapsamı** — Cobaya veya MontePython seçimi; veri/nuisance/prior/covariance/likelihood sürümleri sabit. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g6b"></a>
### G6B — Önsel öngörü ve profil taramaları

**Durum:** TODO · **Ön koşul:** G6A · **Cihaz sırası:** MACM6

Zincir öncesinde kararsız bölgeleri ve dejenere parametreleri elemek.

**Kapanış ölçütü:** Spektrum ve fizik ön filtreleri, duyarlı birleşimler ve degeneracy kontrolleri.

**Koşullu kaynak:** Ölçülen ihtiyaç ve bütçeyle küçük CLOUD CPU.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G6B | **Tam gate kapsamı** — Spektrum ve fizik ön filtreleri, duyarlı birleşimler ve degeneracy kontrolleri. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g6c"></a>
### G6C — Tam çıkarım

**Durum:** TODO · **Ön koşul:** G6B · **Cihaz sırası:** CLOUD CPU → MACM6 tanılar

Yalnız fiziksel ön filtreden geçmiş bölgede posterior örneklemek.

**Kapanış ölçütü:** Yakınsama, effective sample size, bağımsız restart ve nuisance kararlılığı; tekrarlanabilir likelihood.

**Koşullu kaynak:** CLOUD hâlen kapalı; göreve özel açık bütçe olmadan çalıştırılamaz.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G6C | **Tam gate kapsamı** — Yakınsama, effective sample size, bağımsız restart ve nuisance kararlılığı; tekrarlanabilir likelihood. | TODO · plan | [ ] | N/A | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g6d"></a>
### G6D — Sağlamlık

**Durum:** TODO · **Ön koşul:** G6C · **Cihaz sırası:** CLOUD CPU → MACM6

Sonucu veri/önsel/tolerans/üretim belirsizliklerine karşı yeniden sınamak.

**Kapanış ölçütü:** Önsel varyasyonu, seçilmiş veri çıkarma, tolerans sıkılaştırma ve üretim katsayılarının belirsizlik yayılımı.

**Koşullu kaynak:** Yalnız onaylı CLOUD CPU kampanyası.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G6D | **Tam gate kapsamı** — Önsel varyasyonu, seçilmiş veri çıkarma, tolerans sıkılaştırma ve üretim katsayılarının belirsizlik yayılımı. | TODO · plan | [ ] | N/A | [ ] | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

<a id="g6e"></a>
### G6E — Nihai uygulanabilirlik dosyası

**Durum:** TODO · **Ön koşul:** G6D · **Cihaz sırası:** MACM6

On bilimsel soruyu kanıtlarıyla cevaplayıp nihai etiketi atamak.

**Kapanış ölçütü:** Varlık, kararlılık, çözülme/çarpışma/üretim, dalga/isocurvature, DE ömrü, tuning, Boltzmann ve posterior; dört resmi final etiketi.

| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |
|---|---|---|---|---|---|---|
| G6E | **Tam gate kapsamı** — Varlık, kararlılık, çözülme/çarpışma/üretim, dalga/isocurvature, DE ömrü, tuning, Boltzmann ve posterior; dört resmi final etiketi. | TODO · plan | [ ] | N/A | N/A | Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor |

## Şimdi doğrulanmış başlıca sonuçlar

| Sonuç | Ölçüm ve kapsam | Kanıt |
|---|---|---|
| Hopf yükü | Q=−1.000000004972 (49³ bağımsız başlangıç alanı; durağan çözüm değil) | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md>), [RTX5070 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md>) |
| İndirgenmiş vakum smoke artığı | 2.71e−9; birim sektör durağan soliton iddiası yok | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T05__G0B-T05__MACM6__20261003T100609Z__d3106d3__f7f8faca__REPORT.md>) |
| Tam M ağır-limit enerji farkı | 1.00e−15; CPU referans hazırlığı | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G1\G1A-T04__G1A-T04__MACM6__20261003T102101Z__5f01a82__771488e7__REPORT.md>) |
| Operatör bazı | 32 d≤4 karanlık/metrik operatör; IBP kapsamı | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4A-T01__G4A-T01__MACM6__20261001T193427Z__8e637b1__f5f125f4__REPORT.md>) |
| Tek döngü switching | Daha düşük ikinci-derece λ²C2² karşı terimi doğrulandı; baseline değiştirilmedi | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4B-T01__G4B-T01__MACM6__20261003T103247Z__d64b18b__39461767__REPORT.md>) |
| Düz uzay bounce | Bhat4=1082.94755553; kaynakla bağıl fark 4.94e−9; fiziksel ömür değil | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4D-T04__G4D-T04__MACM6__20261003T103854Z__ffaee76__f64c5f3a__REPORT.md>) |
| RTX5070 gerçek CUDA aynaları | G0A-T02/G0B-T01/G0B-T02 PASS; float64, PyTorch 2.11.0+cu128, driver 616.92; durağan çözücü/fiziksel spektrum değil | [MACM6 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__REPORT.md>), [RTX5070 raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__REPORT.md>) |

## Eksik girdiler ve bekleme nedenleri

| Girdi | Etkilenen gate’ler | Gereken |
|---|---|---|
| RTX5070 üretim ve hassasiyet ölçümleri | G0B-T03/T04, G0C; ardından G1/G2 | İlk üç CUDA aynası ve gerçek ortam doğrulandı. Durağan üretim sürücüsü, fiziksel spektrum, büyük grid bellek/süre ve hassasiyet profili hâlâ bekliyor. |
| Yeniden üretilmiş durağan alan/spektrum | G0B-T03/T04; G1A/B/C/D | Durağan checkpoint ve fiziksel özçiftler; mevcut kompakt checkpoint nonstationary |
| Somut L_m, fiziksel ölçek ve UV matching | Tam G4B/G4C; G3 portal sınırları | f/Lambda_U/sigma0/m_chi/portal Lambda; kesim ve eşleşme koşulları |
| Çarpışma ve üretim sonuçları | G1G, G2F, G3, G5, G6 | Kütle/boyut/βH, kesitler, bolluk, dağılım ve ölçülen closure katsayıları |
| Korunmuş bölge, yerçekimli bounce ve prefaktör | G4D/G4E | Fiziksel vakum ömrü ve GMH/RH değerlendirmesi |
| Gate bazlı açık CLOUD bütçesi | G1/G2 kampanyaları; G6 zincirleri | Şu an paused=true, onaylı gate yok ve USD 0; kendiliğinden açılmaz |

## Gate 0’da RTX5070 beklemeden kalan MACM6 işleri

Kayıtlı referans/hazırlıkların tamamlanması Gate 0’ın genel kapsamını tüketmemiştir. Bu iki kaynak benchmark’ı henüz ayrı görev/config/rapor olarak kaydedilmedi; TODO plan kapsamıdır. Kaynak hedefleri ve sınırlar: [G0 kapsam denetimi](<C:\Users\Death\Desktop\viability-test-for-fock-main\docs\G0_MACM6_REMAINING.md>).

| İş | Kaynak ve kabul kapsamı | Durum | Cihaz |
|---|---|---|---|
| Homojen tetikleme benchmark’ı | Bölüm9 Eq.76–88; eşik/kararlılık/iş dengesi; reçeteli banyo, kapalı üretim değil | TODO · plan | MACM6 |
| İndirgenmiş pertürbasyon/büyüme benchmark’ı | Bölüm11.4 Eq.114–118 / Table4; yayın örnek girdileri; tam Boltzmann değil | TODO · plan | MACM6 |

## Geçmiş hatalar ve düzeltmeler

Aktif FAIL/BLOCKED görevler yukarıdaki canlı kayıttadır. Aşağıdaki uygulama/kayıt hataları korundu ve tekrar doğrulamayla giderildi; sağlam bir fiziksel kararsızlık olarak sınıflandırılmadı.

| Görev | Giderilen sorun | Korunan hata raporu | Son durum |
|---|---|---|---|
| G0A-T03 | İlk SciPy/macOS yükleyici hatası; düzeltilmiş ortamla PASS. | [FAIL raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T03__G0A-T03__MACM6__20261001T173933Z__cfdc4e2__a64a600a__REPORT.md>) | PASS |
| G0B-T02 | CUDA validator called detach() on already-converted NumPy arrays and host scalar comparisons, before returning topology metrics. | [FAIL raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0B-T02__G0B-T02__RTX5070__20261003T203311Z__76afab1__23ad6ac8__REPORT.md>) | PASS |
| G4A-T01 | Test fixture ayar dizini eksikti; aynı ölçütlerle düzeltme ve PASS. | [FAIL raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4A-T01__G4A-T01__MACM6__20261001T193144Z__ad63bfb__f5f125f4__REPORT.md>) | PASS |
| G4A-T02 | NumPy bool değerinin sonuç kaydı hatası; dönüşüm düzeltildi ve PASS. | [FAIL raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G4\G4A-T02__G4A-T02__MACM6__20261003T102541Z__3654d66__59ca8890__REPORT.md>) | PASS |
| G0A-T04 | Eski raporlar seal öncesi biçimdeydi; özgün artifact hash denetimiyle PASS. | [FAIL raporu](<C:\Users\Death\Desktop\viability-test-for-fock-main\reports\G0\G0A-T04__G0A-T04__MACM6__20261003T104520Z__7a1d549__32d67550__REPORT.md>) | PASS |

## Ortam, aktarım ve bir sonraki cihaz

- Python hedefi 3.12; MACM6 bağımlılıkları [sabitlenmiş ortam](<C:\Users\Death\Desktop\viability-test-for-fock-main\requirements\macm6.freeze.txt>).
- Kaynak PDF ve checkpoint kimlikleri [kaynak manifesti](<C:\Users\Death\Desktop\viability-test-for-fock-main\config\benchmark\publication.source.yaml>) ve [cihaz devir notu](<C:\Users\Death\Desktop\viability-test-for-fock-main\MACHINE_HANDOFF.md>) içinde.
- MACM6 hazırlık kapsamı: [tamamlama özeti](<C:\Users\Death\Desktop\viability-test-for-fock-main\docs\MACM6_COMPLETION_SUMMARY.md>).
- Sıradaki tek eylem: [NEXT](<C:\Users\Death\Desktop\viability-test-for-fock-main\NEXT.md>); cihaz kurulum/devam adımları: [RTX5070 hazırlık notu](<C:\Users\Death\Desktop\viability-test-for-fock-main\docs\RTX5070_READY.md>).
- Cihazlar arası proje devamı ve mevcut checkpoint kapsamı: [pratik geçiş rehberi](<C:\Users\Death\Desktop\viability-test-for-fock-main\docs\DEVICE_CONTINUATION.md>).
- Doğrulanmış offline paket: [RTX5070 ZIP](<C:\Users\Death\Desktop\viability-test-for-fock-main\transfers\RTX5070__20261003T144940Z__9da2c46.zip>) (2412068 byte); kaynak Git snapshot `9da2c4641a8fa21394a2e7e1bbb29d571dfc7cb1`.
- Paket SHA256: `b600fbb9cab9e2717754a320c4444e33aa662612de6e73137e45a46c3bc137b5`; ayrı receipt: [aktarım kaydı](<C:\Users\Death\Desktop\viability-test-for-fock-main\docs\RTX5070_TRANSFER_PACKET.md>).
- Her ZIP kaynak Git snapshotını taşır; kendi aktarım receipt'i sonradan kaydedilir. Son paket seçimi için güncel aktarım kaydını, geri yüklemede TRANSFER.json'daki commit ve dosya hash'lerini kullanın.
- Git remote ve uzak runner kurulumu yok; G0D opsiyonel ve kapalı. CLOUD otomatik açılmaz.
