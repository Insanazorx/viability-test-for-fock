# Gate 0 — RTX5070 beklemeden kalan MACM6 kapsamı

Kapsam denetimi: 2026-10-03. Kaynak: AGENTS.md Gate 0 genel hedefi ve
SHA256 kimliği sabit `yayınlanan.pdf`, bölüm 9 ve bölüm 11.4.

Önceki tamamlama kaydı, kayıtlı CPU çekirdek/spektral/Hopf/çözücü/HVP
referansları ve mevcut-girdi hazırlık paketine aittir. Gate 0 genel hedefindeki
aşağıdaki iki yayın benchmark'ı yürütme kaydına dahil edilmemiştir. Bu denetim
bir bilimsel FAIL sonucu veya mevcut PASS raporlarının iptali değildir.

## 1. Homojen tetikleme benchmark'ı — yapılmadı

- Kaynak: bölüm 9, sayfa 10–12, Eq.76–88, Fig.4.
- MACM6, SciPy ODE ile yayımlanan q/chi/lambda sistemi ve verilen başlangıç
  değerlerini çözebilir. Yayının reçeteli madde banyosu ve sabit H'ı kullanılır.
- Eşik geçişi, son lambda, kinetik/gradyan kararlılık katsayıları ve açık sistem
  iş dengesi karşılaştırılır; zaman adımı/tolerans ve belirtilen ±%5 hassasiyet
  kontrolleri ayrı raporlanır.
- Mevcut durağan Hopf checkpoint'i veya ölçülmüş soliton/üretim sonucu gerekmez.
- Bilimsel kapsam: yayın benchmark'ı tekrarı. G2A'daki kapalı FLRW enerji
  muhasebesi ve üretim gate'ini kapatmaz.

## 2. İndirgenmiş pertürbasyon benchmark'ı — yapılmadı

- Kaynak: bölüm 11.3–11.4, sayfa 14–15, Eq.114–118, Table4 ve Fig.5.
- Verilen referans arka plan, beta_H=0.02, m_lambda,f=5H0, c_H²=1e−9 ve
  sigma_H=0 ile iki bileşenli büyüme ODE'leri MACM6'da çözülebilir.
- Üç k noktasının kuvvet/büyüme oranları eşlenmiş uncoupled baselinela,
  adyabatik büyüyen başlangıç koşulları ve tolerans yakınsamasıyla karşılaştırılır.
- Bu değerler yayının örnek closure girdileridir; RTX5070'den beta_H ölçümü veya
  üretim katsayıları gelmesini beklemek yayın örneği tekrarı için gerekmez.
- Bilimsel kapsam: indirgenmiş aday düzeyi tekrar. G5 tam Boltzmann ve G6
  likelihood uygulanabilirliği PASS sayılmaz.

## Ek mühendislik hazırlıkları — zorunlu/acil RTX kullanımı yok

Kolektif modların sınır koşuluna uygun analitik kataloğu, küçük sentetik
problemlerde Lanczos/LOBPCG doğrulaması ve optimizer/AL/RNG durumunu birlikte
kaydetme-sürdürme desteği MACM6'da hazırlanabilir. Gerçek durağan çözümlerin
fiziksel düşük spektrumu ve CUDA hassasiyet/bellek/süre ölçümleri RTX5070 ister.

Bu iki benchmark ve ek hazırlıklar henüz çalıştırılmadı. Devamda önce ayrı
MACM6 görevi/ayarları, kaynak eşlemesi ve kabul ölçütleri kaydedilir; sonra
kimlikli çalışma ve tek substep raporu üretilir. RTX5070 ertelemesi korunur,
mevcut G0B-T03/T04 ve G0C-T01/T02 kutuları değiştirilmez.

Pratik sıra: homojen tetikleme tekrarı, ardından indirgenmiş büyüme tekrarı.
RTX5070 boş olduğunda ilk cihaz görevi yine G0A-T02 CUDA aynasıdır. GPU'yu
bu iki MACM6 çalışmasından önce kullanmayı gerektiren acil bir durum yoktur.
