"""Full contract dashboard; display plans never become executable task state."""
from collections import Counter
from pathlib import Path
import re
from common import MACHINES


def validate_roadmap(state):
    roadmap=state.get('roadmap')
    if roadmap is None:return
    if roadmap.get('schema_version')!=1:raise ValueError('Invalid roadmap schema')
    stages=roadmap['stages'];ids=[stage['id'] for stage in stages]
    if len(ids)!=len(set(ids)) or any(not re.fullmatch(r'G[0-6][A-G]',key) for key in ids):
        raise ValueError('Invalid/duplicate roadmap stage')
    main_ids=[gate['id'] for gate in roadmap['main_gates']]
    if len(main_ids)!=len(set(main_ids)) or any(key[:2] not in main_ids for key in ids):
        raise ValueError('Roadmap main gate missing/duplicated')
    rows=[]
    for stage in stages:
        if set(stage['prerequisites'])-set(ids):raise ValueError('Unknown roadmap dependency')
        for row in stage['tasks']:
            if row['kind'] not in {'contract','full_scope','preparation','scoped'}:
                raise ValueError('Invalid dashboard scope kind')
            if not row['id'].startswith(stage['id']):raise ValueError('Roadmap row belongs to another stage')
            if set(row['machine_order'])-set(MACHINES) or not row['machine_order']:
                raise ValueError('Invalid planned machine responsibility')
            if row['kind']=='full_scope' and row['id']!=stage['id']:
                raise ValueError('Unnamed contract scope must keep its stage ID')
            rows.append(row['id'])
    if len(rows)!=len(set(rows)):raise ValueError('Duplicate roadmap row')
    if set(state['tasks'])-set(rows):raise ValueError('Registered task omitted from dashboard')


def stage_status(stage,state):
    registered=[state['tasks'][row['id']] for row in stage['tasks'] if row['id'] in state['tasks']]
    if any(t['status']=='FAIL' for t in registered):return 'FAIL'
    if any(t['status']=='BLOCKED' for t in registered):return 'BLOCKED'
    primary=[row for row in stage['tasks'] if row['kind']=='contract']
    if primary and all(state['tasks'].get(row['id'],{}).get('status')=='PASS' for row in primary):return 'PASS'
    if stage['optional'] and not any(t['enabled'] for t in registered):return 'DISABLED'
    if any(t['status'] in {'PASS','CLAIMED','RUNNING'} for t in registered):
        return 'PREPARED' if primary and not any(state['tasks'].get(row['id'],{}).get('status') in {'PASS','CLAIMED','RUNNING'} for row in primary) else 'PARTIAL'
    return 'TODO'


def cell(value):
    return str(value).replace('|','\\|').replace('\n',' ')


def link(root,path,label):
    return f'[{label}](<{root / path}>)'


def evidence(root,task):
    return ', '.join(link(root,task['machine_reports'][m],m+' raporu')
                     for m in MACHINES if task.get('machine_reports',{}).get(m)) or 'Rapor yok'


def task_flags(row,state):
    task=state['tasks'].get(row['id'])
    order=task['machine_order'] if task else row['machine_order']
    return [('[X]' if task and task['machine_done'][m] else '[ ]') if m in order else 'N/A' for m in MACHINES]


def build_status(state,current,waiting,root):
    """Pure rendering: no new task, completion flag, report or NEXT mutation."""
    root=Path(root);validate_roadmap(state)
    roadmap=state.get('roadmap');tasks=state['tasks'];counts=Counter(t['status'] for t in tasks.values())
    dashboard=state.get('dashboard',{});program=state.get('macm6_program',{})
    action=current or waiting
    key=action[0] if action else None
    machine=next((m for m in action[1]['machine_order'] if not action[1]['machine_done'][m]),None) if action else None
    lines=['# STATUS — Fock-selected dark-sector programı','',
           'Bu görünüm `state/state.yaml` dosyasından üretilir. Güncellemek için `scripts/ctl.py refresh`; elle değiştirilmez.','',
           f"Durum kaydı (UTC): **{state.get('updated_utc','N/A')}**",'',
           '## Genel durum','',
           '| Başlık | Şu anki durum |','|---|---|',
           f"| Bilimsel sonuç | **{dashboard.get('overall_scientific_label','PARTIAL / UNRESOLVED')}** |",
           f"| Işınımsal değerlendirme | {cell(dashboard.get('radiative_assessment','Henüz değerlendirilmedi'))} |",
           f"| MACM6 | {('Kayıtlı CPU referans/hazırlıkları tamam; G0 kapsam denetiminde iki RTX-bağımsız yayın benchmark’ı henüz yapılmamış bulundu.' if dashboard.get('g0_cpu_remaining') else 'Mevcut girdilerle yapılabilen bağımsız hazırlık tamamlandı; sonraki analizler yeni sonuç/girdi bekliyor.' if program.get('status')=='AVAILABLE_INPUT_WORK_COMPLETE' else 'Kayıtlı görev tablosuna bakın.')} |",
           f"| Sıradaki tek eylem | {key or 'Görev kaydı incelenecek'} / {machine or 'N/A'}{(' — DEFERRED; çalışma başlatılmadı' if waiting else '')} |",
           f"| CLOUD | {'PAUSED' if state['cloud']['paused'] else 'APPROVED'}; onaylı gate: {state['cloud'].get('approved_gate') or 'yok'}; çalışma başına USD {state['cloud']['max_usd_per_run']} |",
           f"| Yürütme kaydı | {len(tasks)} görev: {counts['PASS']} PASS, {counts['RUNNING']} RUNNING, {counts['CLAIMED']} CLAIMED, {counts['TODO']} TODO, {counts['FAIL']} FAIL, {counts['BLOCKED']} BLOCKED, {counts['ARCHIVED']} ARCHIVED |",'',
           '**Okuma anahtarı:** `[X]` yalnız ilgili cihazın raporlu sorumluluğunun tamamlandığını, `[ ]` beklediğini, `N/A` o cihazın atanmadığını gösterir. `RUNNING` görev yaşam-durumudur; ertelenmiş bir görevin hesabı şu anda çalışıyor anlamına gelmez.','',
           '`PASS · hazırlık` ve `PASS · kısmi kapsam` özgün bilimsel gate’i kapatmaz. `TODO · plan` satırları sözleşmedeki gelecek işlerdir; yürütme kaydına veya çalıştırma kuyruğuna eklenmiş değildir. `Ön koşul bekliyor` ifadesi raporlu `BLOCKED` sonucu değildir.','',
           '**Alt gate durumları:** `PASS` tanımlı kapsamın tamamlandığını, `PARTIAL` kısmi ilerlemeyi, `PREPARED` ön hazırlığın yapıldığını, `TODO` işin beklediğini, `DISABLED` isteğe bağlı işin kapalı olduğunu gösterir. Plan satırlarındaki cihaz kutuları gelecekteki sorumluluğu belirtir; CLOUD kutusu bütçe veya çalıştırma onayı değildir.','',
           '## Öncelikli kalan işler','',
           'Bunlar yürütme kaydındaki etkin, tamamlanmamış işlerdir. Gelecek G0–G6 kapsamı aşağıdaki gate tablolarında ayrıca gösterilir.','',
           '| Görev | Kalan iş | Durum | Cihaz sırası | Ön koşullar |','|---|---|---|---|---|']
    rows={row['id']:row for stage in (roadmap or {}).get('stages',[]) for row in stage['tasks']}
    for task_id,t in tasks.items():
        if t['enabled'] and t['status'] not in {'PASS','ARCHIVED'}:
            title=rows.get(task_id,{}).get('title',t['title'])
            deps=', '.join(f"{dep}: {tasks[dep]['status']}" for dep in t['prerequisites']) or 'Yok'
            lines.append('| '+' | '.join(cell(v) for v in
                         (task_id,title,t['status'],' → '.join(t['machine_order']),deps))+' |')
    if dashboard.get('g0_cpu_remaining'):
        lines.extend(['','Ayrıca MACM6 üzerinde homojen tetikleme ve azaltılmış pertürbasyon benchmark’ları **TODO · plan**. Henüz ayrı yürütme kaydı/config/rapor yok; G0 genel kapanışı bekliyor.'])
    lines.extend(['','İsteğe bağlı G0D runner işleri kapalıdır. Hazırlık raporları durağan çözüm/Hessian veya bilimsel gate kapanışı değildir.','',
                  '## Cihazların durumu','',
                  '| Cihaz | Raporlu tamamlanan sorumluluk | Operasyon durumu |','|---|---|---|'])
    for m in MACHINES:
        scheduling=state.get('machine_scheduling',{}).get(m,{})
        status=('Kapalı; açık bütçe ve ölçülen kaynak gereği olmadan iş yok.' if m=='CLOUD' else
                'DEFERRED — '+scheduling['reason'] if scheduling.get('deferred') else
                'Kayıtlı hazırlık tamam; iki RTX-bağımsız G0 benchmark’ı ayrı görev/ayar/rapor bekliyor.' if m=='MACM6' and dashboard.get('g0_cpu_remaining') else
                'Mevcut-girdi programı tamamlandı; yeni GPU/model girdileriyle analiz devam edecek.' if m=='MACM6' and program.get('status')=='AVAILABLE_INPUT_WORK_COMPLETE' else 'Kayıtlı görev sırası geçerli.')
        lines.append(f"| {m} | {sum(t['machine_done'][m] for t in tasks.values())} | {cell(status)} |")
    verified=dashboard.get('last_verified_unit_suite')
    if verified:lines.extend(['',f"Son raporla belgelenmiş tam test paketi: **{verified['tests']} PASS** — "+link(root,verified['report'],'doğrulama raporu')+'.'])
    if not roadmap:
        lines.extend(['','## Kayıtlı görevler','','| Görev | Durum | MACM6 | RTX5070 | CLOUD |','|---|---|---|---|---|'])
        for key,t in tasks.items():
            row={'id':key,'machine_order':t['machine_order']}
            lines.append('| '+' | '.join([key,t['status'],*task_flags(row,state)])+' |')
        return '\n'.join(lines)+'\n'
    stages=roadmap['stages'];statuses={v['id']:stage_status(v,state) for v in stages}
    main_status={}
    for gate in roadmap['main_gates']:
        required=[statuses[v['id']] for v in stages if v['id'][:2]==gate['id'] and not v['optional']]
        main_status[gate['id']]=('FAIL' if 'FAIL' in required else 'BLOCKED' if 'BLOCKED' in required else
                                'PASS' if all(v=='PASS' for v in required) else
                                'PARTIAL' if any(v in {'PASS','PARTIAL','PREPARED'} for v in required) else 'TODO')
    if dashboard.get('g0_cpu_remaining') and main_status.get('G0')=='PASS':
        main_status['G0']='PARTIAL'
    lines.extend(['','## Bütün ana gate’lerin özeti','',
                  '| Gate | Amaç | Genel sonuç | Alt gate durumu |','|---|---|---|---|'])
    for gate in roadmap['main_gates']:
        detail=', '.join(f"[{v['id']}](#{v['id'].lower()}) {statuses[v['id']]}" for v in stages if v['id'][:2]==gate['id'])
        lines.append(f"| [{gate['id']}](#{gate['id'].lower()}) | {gate['title']} | **{main_status[gate['id']]}** | {detail} |")
    mandatory=[v for v in stages if not v['optional']]
    complete=sum(statuses[v['id']]=='PASS' for v in mandatory)
    lines.extend(['',f"Ana gate kapanışı: **{sum(v=='PASS' for v in main_status.values())}/7**. Tam kapsamı tamamlanan zorunlu alt gate: **{complete}/{len(mandatory)}**; ayrıca isteğe bağlı G0D kapalı. Görev sayıları veya hazırlıklar bilimsel ilerleme yüzdesi olarak kullanılmaz.",
                  '',f"Kapsam: **{len(stages)} alt gate**, AGENTS.md’de açıkça numaralandırılmış **{sum(row['kind']=='contract' for v in stages for row in v['tasks'])} görev**, ayrıca raporlu hazırlık/kısmi kapsam kayıtları. T-ID tanımlanmayan gate’ler tam kapsam satırıyla görünür; yeni görev ID’si uydurulmaz.",'',
                  '## Bağımlılık haritası','',
                  '```text','G0A → G0B → G0C → G0D (isteğe bağlı)',
                  'G0B → G1A → G1B → G1C → G1D',
                  '                 └→ G1E → G1F → G1G',
                  'G1B + G1E → G2A → G2B → G2C → G2D → G2E → G2F',
                  'G1G + G2F → G3A → G3B → G3C → G3D',
                  'G0A → G4A → G4B → G4C → G4E',
                  'G1B → G4D; G1B ölçümleri → G4E kompaktlık',
                  'G2F + G3D + G4C + G4D → G5A → G5B → G5C → G5D → G5E',
                  'G5E → G6A → G6B → G6C → G6D → G6E','```','',
                  'G4 teori hattı erken ve paralel ilerleyebilir. Hazırlık görevleri bu bilimsel bağımlılıkları kaldırmaz. Bulut gerekliliği ve bütçesi ayrı kontrol edilir.'])
    for gate in roadmap['main_gates']:
        lines.extend(['',f"<a id=\"{gate['id'].lower()}\"></a>",f"## {gate['id']} — {gate['title']}",''])
        for v in (v for v in stages if v['id'][:2]==gate['id']):
            lines.extend([f"<a id=\"{v['id'].lower()}\"></a>",f"### {v['id']} — {v['title']}",'',
                          f"**Durum:** {statuses[v['id']]} · **Ön koşul:** {', '.join(v['prerequisites']) or 'Başlangıç'} · **Cihaz sırası:** {v['route']}",'',
                          v['goal'],'',f"**Kapanış ölçütü:** {v['acceptance']}"])
            if v['note']:lines.extend(['',f"**Kapsam notu:** {v['note']}"])
            if v['conditional']:lines.extend(['',f"**Koşullu kaynak:** {v['conditional']}"])
            lines.extend(['','| Görev | İş / kabul ölçütü | Durum | MACM6 | RTX5070 | CLOUD | Kanıt / kalan iş |','|---|---|---|---|---|---|---|'])
            for row in v['tasks']:
                t=tasks.get(row['id']);kind=row['kind'];status=t['status'] if t else 'TODO · plan'
                if t and kind in {'preparation','scoped'}:status+=' · '+('hazırlık' if kind=='preparation' else 'kısmi kapsam')
                if t and not t['enabled']:status+=' · kapalı'
                if t:
                    pending=next((m for m in t['machine_order'] if not t['machine_done'][m]),None)
                    if pending and state.get('machine_scheduling',{}).get(pending,{}).get('deferred'):status+=' · '+pending+' ertelendi'
                proof=evidence(root,t) if t else 'Yürütme kaydı/rapor yok; ön koşul veya girdi bekliyor'
                if row.get('note'):proof+='; '+row['note']
                description=f"**{row['title']}** — {row['acceptance']}"
                lines.append('| '+' | '.join([row['id'],cell(description),cell(status),*task_flags(row,state),cell(proof)])+' |')
            lines.append('')
    lines.extend(['## Şimdi doğrulanmış başlıca sonuçlar','',
                  '| Sonuç | Ölçüm ve kapsam | Kanıt |','|---|---|---|'])
    for result in dashboard.get('key_results',[]):
        t=tasks[result['task']]
        lines.append(f"| {result['label']} | {cell(result['value'])} | {evidence(root,t)} |")
    lines.extend(['','## Eksik girdiler ve bekleme nedenleri','',
                  '| Girdi | Etkilenen gate’ler | Gereken |','|---|---|---|'])
    for missing in dashboard.get('missing_inputs',[]):
        lines.append('| '+' | '.join(cell(missing[k]) for k in ('input','affected','need'))+' |')
    pending_cpu=dashboard.get('g0_cpu_remaining',[])
    if pending_cpu:
        lines.extend(['','## Gate 0’da RTX5070 beklemeden kalan MACM6 işleri','',
                      'Kayıtlı referans/hazırlıkların tamamlanması Gate 0’ın genel kapsamını tüketmemiştir. Bu iki kaynak benchmark’ı henüz ayrı görev/config/rapor olarak kaydedilmedi; TODO plan kapsamıdır. Kaynak hedefleri ve sınırlar: '+link(root,'docs/G0_MACM6_REMAINING.md','G0 kapsam denetimi')+'.','',
                      '| İş | Kaynak ve kabul kapsamı | Durum | Cihaz |','|---|---|---|---|'])
        for item in pending_cpu:
            lines.append('| '+' | '.join(cell(item[key]) for key in ('title','scope','status','machine'))+' |')
    lines.extend(['','## Geçmiş hatalar ve düzeltmeler','',
                  'Aktif FAIL/BLOCKED görevler yukarıdaki canlı kayıttadır. Aşağıdaki uygulama/kayıt hataları korundu ve tekrar doğrulamayla giderildi; sağlam bir fiziksel kararsızlık olarak sınıflandırılmadı.','',
                  '| Görev | Giderilen sorun | Korunan hata raporu | Son durum |','|---|---|---|---|'])
    for key,t in tasks.items():
        previous=t.get('recovery',{}).get('previous_failure_report')
        if previous:
            note=dashboard.get('history_notes',{}).get(key,t['recovery'].get('reason',t['recovery'].get('cause','Kayıtlı düzeltme')))
            lines.append(f"| {key} | {cell(note)} | {link(root,previous,'FAIL raporu')} | {t['status']} |")
    lines.extend(['','## Ortam, aktarım ve bir sonraki cihaz','',
                  '- Python hedefi 3.12; MACM6 bağımlılıkları '+link(root,'requirements/macm6.freeze.txt','sabitlenmiş ortam')+'.',
                  '- Kaynak PDF ve checkpoint kimlikleri '+link(root,'config/benchmark/publication.source.yaml','kaynak manifesti')+' ve '+link(root,'MACHINE_HANDOFF.md','cihaz devir notu')+' içinde.',
                  '- MACM6 hazırlık kapsamı: '+link(root,'docs/MACM6_COMPLETION_SUMMARY.md','tamamlama özeti')+'.',
                  '- Sıradaki tek eylem: '+link(root,'NEXT.md','NEXT')+'; cihaz kurulum/devam adımları: '+link(root,'docs/RTX5070_READY.md','RTX5070 hazırlık notu')+'.'])
    lines.append('- Cihazlar arası proje devamı ve mevcut checkpoint kapsamı: '+link(root,'docs/DEVICE_CONTINUATION.md','pratik geçiş rehberi')+'.')
    packet=program.get('transfer_packet')
    if packet:
        lines.extend(['- Doğrulanmış offline paket: '+link(root,packet['path'],'RTX5070 ZIP')+f" ({packet['bytes']} byte); kaynak Git snapshot `{packet['git_commit']}`.",
                      f"- Paket SHA256: `{packet['sha256']}`; ayrı receipt: "+link(root,'docs/RTX5070_TRANSFER_PACKET.md','aktarım kaydı')+'.',
                      '- Her ZIP kaynak Git snapshotını taşır; kendi aktarım receipt\'i sonradan kaydedilir. Son paket seçimi için güncel aktarım kaydını, geri yüklemede TRANSFER.json\'daki commit ve dosya hash\'lerini kullanın.'])
    history=state.get('repository_history')
    if history:
        lines.extend(['','## Geri alınan MACM6 Git geçmişi','',
                      f"- Denetim: **{history['status']}**; UTC `{history['verified_utc']}`; "+link(root,history['audit_report'],'bundle doğrulama raporu')+'.',
                      f"- `{history['bundle_path']}`: {history['bundle_bytes']} byte; SHA256 `{history['bundle_sha256']}`.",
                      f"- `{history['restored_branch']}`: `{history['tip']}`; **{history['commit_count']} commit**. RTX5070 çalışma dalı `{history['current_branch']}` korunmuştur.",
                      f"- {history['macm6_reports_byte_identical']} MACM6 tamamlama raporu, {history['original_evidence_files_byte_identical']} eski kanıt dosyası ve {history['frozen_configs_byte_identical']} config byte-identical; {history['historical_run_commits_available']} eski çalışma commit’i erişilebilir.",
                      '- Git bundle bütünlüğü ve kayıtlı aktarım commit’i doğrulandı. TRANSFER.json/bağımsız bundle SHA256 manifesti bu klasörde yok; yukarıdaki SHA256 bu denetimde ölçüldü, dış manifest eşleşmesi iddia edilmez.',
                      '- Bundle kod/geçmiş içerir; durağan yayın checkpoint’i veya arşivlenmiş üretim initializer’ı sağlamaz. Sayısal kabul ölçütleri ve cihaz tamamlanma bayrakları değişmedi.',
                      '- Git remote: '+f"[GitHub deposu]({history['remote']}); iki geçmiş ayrı dallarda korunur, main geçmişi yeniden yazılmaz."])
    else:
        lines.append('- Git remote/geçmiş için mevcut cihaz devir notunu kullanın.')
    lines.extend(['- Uzak runner kurulumu yok; G0D opsiyonel ve kapalı. CLOUD otomatik açılmaz.',''])
    return '\n'.join(lines)
