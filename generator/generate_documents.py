from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "documents" / "source"
PDF_DIR = ROOT / "documents" / "pdf"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

CSS = r"""
@page { size: A4; margin: 23mm 18mm 21mm 18mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  color: #1b2730;
  font-family: "Noto Sans CJK JP", "Noto Sans JP", sans-serif;
  font-size: 10.5pt;
  line-height: 1.65;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.fixed-header {
  position: fixed;
  top: -17mm;
  left: 0;
  right: 0;
  height: 12mm;
  border-bottom: 1px solid #78a9b3;
  color: #315c66;
  font-size: 8pt;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.fixed-footer {
  position: fixed;
  bottom: -14mm;
  left: 0;
  right: 0;
  height: 10mm;
  border-top: 1px solid #b8cdd2;
  color: #61757a;
  font-size: 7.5pt;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cover {
  min-height: 225mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  page-break-after: always;
}
.brand { color: #0f6b78; font-size: 11pt; font-weight: 700; letter-spacing: 0.08em; }
h1 { margin: 10mm 0 4mm; font-size: 24pt; line-height: 1.25; color: #0b3d4a; }
.subtitle { font-size: 13pt; color: #526b71; margin-bottom: 12mm; }
.meta-grid {
  display: grid;
  grid-template-columns: 35mm 1fr;
  gap: 0;
  border-top: 2px solid #0f6b78;
  border-bottom: 1px solid #aac7cd;
  width: 100%;
}
.meta-grid div { padding: 3mm 2.5mm; border-bottom: 1px solid #dbe8eb; }
.meta-label { font-weight: 700; background: #eef7f8; color: #315c66; }
h2 { margin: 9mm 0 3mm; padding-bottom: 1.5mm; border-bottom: 2px solid #0f6b78; font-size: 16pt; color: #0b3d4a; page-break-after: avoid; }
h3 { margin: 6mm 0 2mm; font-size: 12.5pt; color: #315c66; page-break-after: avoid; }
p { margin: 0 0 3mm; }
ul, ol { margin: 2mm 0 4mm 6mm; padding-left: 5mm; }
li { margin-bottom: 1.5mm; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0 6mm; font-size: 9.2pt; page-break-inside: avoid; }
th { background: #0b3d4a; color: white; text-align: left; padding: 2.6mm 2.4mm; font-weight: 700; }
td { border-bottom: 1px solid #d2e1e4; padding: 2.3mm 2.4mm; vertical-align: top; }
tr:nth-child(even) td { background: #f6fafb; }
.callout { margin: 4mm 0 6mm; padding: 4mm; border-left: 4px solid #d88b2c; background: #fff6e9; page-break-inside: avoid; }
.callout.critical { border-left-color: #b93b3b; background: #fff0f0; }
.callout.info { border-left-color: #0f6b78; background: #eef7f8; }
.kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm; margin: 4mm 0 6mm; page-break-inside: avoid; }
.kpi { border: 1px solid #b9d2d7; border-radius: 2mm; padding: 4mm; background: #f6fbfc; }
.kpi .value { display: block; font-size: 17pt; font-weight: 700; color: #0b3d4a; }
.kpi .label { display: block; font-size: 8.5pt; color: #5d7479; margin-top: 1mm; }
.code { font-family: "Noto Sans Mono CJK JP", monospace; background: #f2f5f6; padding: 3mm; border-radius: 1.5mm; white-space: pre-wrap; font-size: 9pt; }
.page-break { page-break-before: always; }
.small { font-size: 8.7pt; color: #5d6f74; }
.status { display: inline-block; padding: 0.6mm 2mm; border-radius: 8mm; font-size: 8pt; font-weight: 700; background: #dff1e4; color: #27633a; }
.status.warn { background: #fff0d8; color: #855514; }
.status.critical { background: #ffe1e1; color: #8a2929; }
.signature { margin-top: 12mm; display: grid; grid-template-columns: 1fr 1fr; gap: 12mm; }
.signature div { border-top: 1px solid #71878c; padding-top: 2mm; font-size: 8.5pt; }
"""


def esc(value: object) -> str:
    return html.escape(str(value))


def meta_html(meta: dict[str, str]) -> str:
    rows = "".join(f'<div class="meta-label">{esc(k)}</div><div>{esc(v)}</div>' for k, v in meta.items())
    return f'<div class="meta-grid">{rows}</div>'


def table(headers: list[str], rows: list[list[object]]) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def bullets(items: list[str], ordered: bool = False) -> str:
    tag = "ol" if ordered else "ul"
    return f"<{tag}>" + "".join(f"<li>{item}</li>" for item in items) + f"</{tag}>"


def doc_html(doc: dict) -> str:
    meta = doc["meta"]
    header = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>{esc(doc['title'])}</title><style>{CSS}</style></head><body>
<div class="fixed-header"><span>Lakehouse Sound Festival 2026</span><span>{esc(meta['Document ID'])}</span></div>
<div class="fixed-footer"><span>{esc(meta['Classification'])}</span><span>Version {esc(meta['Version'])} / Effective {esc(meta['Effective Date'])}</span></div>
<section class="cover"><div class="brand">NEOTONE FESTIVAL OPERATIONS</div><h1>{esc(doc['title'])}</h1><div class="subtitle">{esc(doc['subtitle'])}</div>{meta_html(meta)}<div class="callout info" style="margin-top:12mm"><strong>架空文書</strong><br>本書はPrivate Agent FactoryおよびAutonomous AI Lakehouseの検証用に作成した完全合成データです。実在のイベント、製品、企業とは関係ありません。</div></section>
"""
    return header + doc["body"] + "</body></html>"


def documents() -> list[dict]:
    common = {"Owner": "Festival Operations Office", "Classification": "Internal / Synthetic Demo"}
    docs: list[dict] = []

    body = """
<h2>1. 目的と適用範囲</h2>
<p>本マニュアルはLakehouse Sound Festival 2026におけるステージ、入場、物販、気象、安全、カスタマーサポートの統括ルールを定める。データ分析結果は運営判断の補助として使用し、重大な安全判断と払い戻し例外は責任者が最終承認する。</p>
<h2>2. インシデント区分</h2>
""" + table(["Severity", "定義", "初動目標", "報告先"], [
        ["CRITICAL", "生命安全または全会場停止に直結", "即時", "Safety Director / Festival Director"],
        ["HIGH", "主要ステージ停止、5,000人以上へ影響", "3分以内", "Festival Operations Center"],
        ["MEDIUM", "局所的なサービス低下、入場・物販の継続的混雑", "5分以内", "Area Manager"],
        ["LOW", "限定的で短時間の影響", "15分以内", "Team Lead"],
    ]) + """
<h2>3. 証拠と記録</h2>
""" + bullets([
        "時刻はすべてAsia/Tokyoで記録する。",
        "数値事実はチケット、入場、センサー、販売、在庫、気象などのシステム記録で確認する。",
        "根本原因はインシデント報告書、サービス情報、保守記録のいずれかで裏付ける。",
        "推測と確認済み事実を明確に分離する。",
        "来場者IDは匿名識別子として扱い、個人情報の復元を試みない。",
    ]) + """
<h2>4. Human-in-the-loop</h2>
<div class="callout critical"><strong>禁止事項</strong><br>AI Agentは、利用者の明示的承認なしに払い戻し確定、タスク登録、設備停止、チケット無効化を実行してはならない。</div>
<h3>4.1 改善タスク</h3>
<p>Agentは分析結果からタスク案を作成できる。登録時はIncident ID、Title、Description、Priority、Owner Teamを提示し、承認後に許可された手続きを実行する。</p>
<h2>5. 改訂履歴</h2>
""" + table(["Version", "Date", "Change"], [["1.1", "2026-06-20", "初版"], ["1.2", "2026-07-05", "入場・気象エスカレーション追加"], ["1.3", "2026-07-15", "AI Agent利用時の承認ルール追加"]])
    docs.append({"title": "Lakehouse Sound Festival 2026 運営統括マニュアル", "subtitle": "役割、インシデント管理、証拠、承認ルール", "meta": {"Document ID": "OPS-GEN-1.3", "Version": "1.3", "Effective Date": "2026-07-15", **common}, "filename": "LSF2026_運営統括マニュアル_v1.3", "body": body})

    body = """
<h2>1. 対象システム</h2>
<p>DJリンクネットワークはDJプレイヤー、DJミキサー、ステージ管理端末、時刻同期サーバーを専用VLANで接続する。各ステージには主系スイッチと予備スイッチを配置する。</p>
<h2>2. 監視閾値</h2>
""" + table(["Metric", "Warning", "Critical", "Required Action"], [
        ["Packet Loss", "2%超が3分", "5%超が2分", "主系を隔離し予備系へ切替"],
        ["Switch Temperature", "70 C以上", "80 C以上", "負荷確認、冷却確認、予備系準備"],
        ["Cooling Fan", "1,500 RPM未満", "1,000 RPM未満", "直ちに予備系へ切替"],
        ["Audio Dropouts", "1分に2回", "1分に3回以上", "DJリンクとプレイヤー状態を同時確認"],
    ]) + """
<h2>3. 障害対応手順</h2>
""" + bullets([
        "NOCは監視画面でパケットロス、温度、ファン回転数を確認する。",
        "DJプレイヤー本体を再起動する前に、スイッチとリンク状態を確認する。",
        "Critical条件を満たした場合、5分以内に予備スイッチへDJリンクVLANを切り替える。",
        "切替後、2台以上のDJプレイヤーで同期、波形更新、音声再生を確認する。",
        "復旧しても対象機器は再利用せず、隔離してベンダー解析へ送る。",
    ], ordered=True) + """
<div class="callout"><strong>注意</strong><br>パケットロスとファン回転数低下が同時に発生している場合、DJプレイヤーの個別故障と断定しない。ネットワーク機器の冷却異常を優先して確認する。</div>
<h2>4. Waveform Arena構成</h2>
""" + table(["Role", "Equipment ID", "Model", "Standby"], [["Main Switch", "EQ-NET-WA-01", "PulseGrid StageLink 48", "EQ-NET-WA-02"], ["DJ Player A", "EQ-DJP-WA-01", "NeoTone PulseDeck M9", "Hot Spare"], ["DJ Player B", "EQ-DJP-WA-02", "NeoTone PulseDeck M9", "Hot Spare"], ["DJ Mixer", "EQ-DJM-WA-01", "NeoTone CrossFlow MX8", "Bypass Input"]]) + """
<h2>5. 記録項目</h2>
<p>Incident ID、障害検知時刻、閾値到達時刻、切替開始・完了時刻、影響公演、対象ロット、保守状況を記録する。</p>
"""
    docs.append({"title": "ステージ音響ネットワーク運用手順", "subtitle": "DJリンク監視、閾値、フェイルオーバー", "meta": {"Document ID": "OPS-NET-2.1", "Version": "2.1", "Effective Date": "2026-07-20", **common}, "filename": "LSF2026_ステージ音響ネットワーク運用手順_v2.1", "body": body})

    body = """
<h2>1. 障害判定</h2>
<p>ゲート端末のスキャン失敗率を5分窓で監視する。QR_TIMEOUT、TOKEN_READ_ERROR、DEVICE_OFFLINEを失敗として扱う。</p>
""" + table(["Level", "Condition", "Action"], [["Observe", "失敗率3%超", "端末別内訳を確認"], ["Warning", "失敗率5%超が3分", "予備端末を起動し係員を配置"], ["Failover", "失敗率7%超が5分", "5分以内にバックアップ端末へ切替"], ["Emergency", "待ち時間30分超", "隣接ゲートへ誘導し運営本部へ報告"]]) + """
<h2>2. バックアップ切替</h2>
""" + bullets([
        "失敗率7%超が5分継続した時点をThreshold Timeとして記録する。",
        "端末再起動を繰り返さず、Threshold Timeから5分以内にバックアップ端末を有効化する。",
        "バックアップ端末はファームウェア1.9.1以上であることを確認する。",
        "切替後は100件以上のスキャンで成功率98%以上を確認する。",
        "待機列が20分を超える場合、Gate AまたはGate Bへ誘導する。",
    ], ordered=True) + """
<h2>3. 既知の互換性</h2>
<p>GateFlow ScanPoint G4のファームウェア1.8.2では、モバイルウォレットで高輝度QRを表示した際にタイムアウト率が上昇する既知事象がある。イベント本番では1.9.1以上を使用する。</p>
<div class="callout critical"><strong>運用基準</strong><br>障害原因の確定を待ってから切り替えるのではなく、サービス影響の閾値を満たした時点で先にフェイルオーバーする。</div>
<h2>4. 改訂履歴</h2>
""" + table(["Version", "Date", "Change"], [["1.0", "2026-06-10", "初版"], ["1.1", "2026-07-02", "失敗率の定義を追加"], ["1.2", "2026-07-18", "5分以内の切替目標とFirmware 1.9.1を追加"]])
    docs.append({"title": "入場ゲート障害対応手順", "subtitle": "QRスキャン障害、待機列、バックアップ切替", "meta": {"Document ID": "OPS-GATE-1.2", "Version": "1.2", "Effective Date": "2026-07-18", **common}, "filename": "LSF2026_入場ゲート障害対応手順_v1.2", "body": body})

    body = """
<h2>1. 基本原則</h2>
<p>払戻はチケット種別、対象日、入場記録、中止内容を組み合わせて判定する。申請理由だけでは自動承認しない。</p>
<h2>2. 悪天候による部分中止</h2>
""" + table(["Ticket Type", "Condition", "Refund"], [
        ["MG_PREMIUM", "指定ヘッドライナーが中止", "アドオン料金100%"],
        ["DAY3", "Day 3入場済み、屋外プログラムが90分超停止", "購入額の15%"],
        ["THREE_DAY", "Day 3入場済み、屋外プログラムが90分超停止", "購入額の5%"],
        ["VIP_THREE_DAY", "Day 3入場済み、屋外プログラムが90分超停止", "購入額の5%"],
        ["入場記録なし", "全日中止ではない場合", "自動返金せず手動確認"],
    ]) + """
<h2>3. 自動判定に必要なデータ</h2>
""" + bullets([
        "ticket_idおよびparent_ticket_id",
        "ticket_type_idと購入金額",
        "対象日のSUCCESS入場ログ",
        "公演のCANCELEDまたはENDED_EARLY状態",
        "悪天候インシデントの継続時間",
    ]) + """
<h2>4. 非対象</h2>
<p>個人的事情、交通遅延、見たい公演の通常の時間変更は自動払戻対象外とする。例外申請はCustomer Supportが手動確認する。</p>
<div class="callout info"><strong>金額計算</strong><br>返金額は100円単位へ丸める。アドオンはアドオン購入額を基準とし、親チケット金額を使用しない。</div>
<h2>5. 承認</h2>
<p>Agentは判定候補と計算根拠を提示できるが、実際の決済返金は承認ワークフローの完了後に行う。</p>
"""
    docs.append({"title": "チケット払戻ポリシー", "subtitle": "悪天候・公演中止時の自動判定条件", "meta": {"Document ID": "TKT-REFUND-2.0", "Version": "2.0", "Effective Date": "2026-07-01", **common}, "filename": "LSF2026_チケット払戻ポリシー_v2.0", "body": body})

    body = """
<h2>1. 監視項目</h2>
<p>SkyWatch Safetyの観測値を15分間隔で収集し、雷距離、平均風速、瞬間風速、降雨量を監視する。</p>
""" + table(["Hazard", "Alert", "Suspend Outdoor Stage", "Resume"], [
        ["Lightning", "15km以内", "10km以内", "20km以上が30分継続"],
        ["Wind Gust", "12m/s以上", "15m/s以上", "10m/s未満が20分継続"],
        ["Rainfall", "10mm/15min以上", "20mm/15min以上", "5mm/15min未満が20分継続"],
    ]) + """
<h2>2. 停止判断</h2>
""" + bullets([
        "いずれかの停止基準に到達した場合、Safety Directorが屋外ステージ停止を宣言する。",
        "停止宣言後3分以内にStage Managerが演奏終了または中断を実施する。",
        "観客を指定の屋内退避エリアへ誘導する。",
        "90分を超える停止が見込まれる場合、Customer Supportへ払戻判定開始を通知する。",
        "再開基準を満たさない限り、人気公演やヘッドライナーであっても再開しない。",
    ], ordered=True) + """
<h2>3. 2026年8月9日の対象</h2>
<p>Modular Garden、Orbit Main Stage、Neon Groove Stageは屋外ステージである。Night Pulse ClubとWaveform Arenaは退避先として使用可能だが、収容上限を超えないよう入場制御する。</p>
<div class="callout critical"><strong>安全優先</strong><br>観客満足度、売上、払戻金額は停止判断の条件に含めない。</div>
"""
    docs.append({"title": "悪天候対応計画", "subtitle": "雷・風・降雨の停止基準と退避運用", "meta": {"Document ID": "WX-PLAN-1.4", "Version": "1.4", "Effective Date": "2026-07-10", **common}, "filename": "LSF2026_悪天候対応計画_v1.4", "body": body})

    body = """
<h2>1. Executive Summary</h2>
<div class="kpi-grid"><div class="kpi"><span class="value">29 min</span><span class="label">Maximum performance delay</span></div><div class="kpi"><span class="value">19.2%</span><span class="label">Maximum packet loss</span></div><div class="kpi"><span class="value">91.8 C</span><span class="label">Maximum switch temperature</span></div></div>
<p>2026年8月8日14:42、Waveform ArenaのDJリンクネットワークで同期切断が発生した。主系スイッチEQ-NET-WA-01の冷却ファン回転数低下に伴い、温度とパケットロスが上昇した。Circuit Bloomを含む3公演に遅延が波及した。</p>
<h2>2. Timeline</h2>
""" + table(["Time", "Event"], [["14:42", "DJプレイヤー間同期切断、波形更新停止"], ["14:46", "パケットロス5%超、温度上昇をNOCが確認"], ["14:51", "予備スイッチへのVLAN切替開始"], ["15:04", "同期と音声再生の復旧確認"], ["15:31", "主系スイッチを隔離しインシデント終了"]]) + """
<h2>3. Data Evidence</h2>
""" + table(["Evidence", "Observed", "Normal"], [["Switch Temperature", "最大91.8 C", "45-55 C"], ["Packet Loss", "最大19.2%", "0.5%未満"], ["Cooling Fan", "最低120 RPM", "2,500-3,000 RPM"], ["Maintenance", "2026-07-25期限、未実施", "高負荷前に完了"]]) + """
<h2>4. Root Cause</h2>
<p><strong>Direct Cause:</strong> 製造ロットNW-2603に該当する冷却ファンの回転数低下。</p>
<p><strong>Contributing Cause:</strong> 交換部品の納入遅延を理由に、2026年7月25日予定の冷却ファン交換を未完了のまま本番運用した。</p>
<p><strong>Not the Root Cause:</strong> DJプレイヤー本体、楽曲ファイル、アーティストのUSBメディア。</p>
<h2>5. Corrective Actions</h2>
""" + bullets(["NW-2603対象機器の即時使用停止と交換", "予防保守期限超過機器を本番構成へ入れないゲートを追加", "Critical閾値到達前の予兆アラートを有効化", "予備スイッチへの切替訓練を各ステージで実施"])
    docs.append({"title": "Waveform Arena 遅延インシデント報告", "subtitle": "DJリンク障害、センサー証拠、根本原因", "meta": {"Document ID": "IR-2026-081", "Version": "1.0", "Effective Date": "2026-08-10", **common}, "filename": "IR-2026-081_Waveform_Arena遅延報告", "body": body})

    body = """
<h2>1. 対象</h2>
<p>PulseGrid StageLink 48の製造ロット<strong>NW-2603</strong>。シリアル番号LSF26-00001からLSF26-00020の一部を含む。</p>
<h2>2. 症状</h2>
""" + bullets(["高負荷時に冷却ファン回転数が断続的に1,000 RPM未満へ低下", "内部温度が80 Cを超過", "ポート間パケットロスが5%以上へ増加", "再起動後に一時復旧するが再発する可能性あり"]) + """
<h2>3. 原因</h2>
<p>ファン制御基板のはんだ接合ばらつきにより、高温時にファン駆動電圧が低下する。ネットワークASIC自体の故障ではない。</p>
<h2>4. 必須対応</h2>
""" + table(["Condition", "Action", "Deadline"], [["NW-2603かつ高負荷イベントで使用", "冷却ファン・制御基板交換", "使用前"], ["交換部品未着", "予備機へ置換", "使用前"], ["運用中に1,000 RPM未満", "5分以内にフェイルオーバーし隔離", "即時"]]) + """
<div class="callout critical"><strong>重要</strong><br>部品待ちを理由に交換を延期したまま高負荷イベントで使用してはならない。</div>
<h2>5. Verification</h2>
<p>交換後、60分の負荷試験で温度70 C未満、ファン2,300 RPM以上、パケットロス0.5%未満を確認する。</p>
"""
    docs.append({"title": "ネットワークスイッチ冷却ファン サービス情報", "subtitle": "PulseGrid StageLink 48 / Lot NW-2603", "meta": {"Document ID": "SB-NW-2603", "Version": "1.1", "Effective Date": "2026-07-12", **common}, "filename": "SB-NW-2603_ネットワークスイッチ冷却ファン通知", "body": body})

    body = """
<h2>1. Summary</h2>
<div class="kpi-grid"><div class="kpi"><span class="value">61.4%</span><span class="label">Failure rate in incident window</span></div><div class="kpi"><span class="value">29.6 min</span><span class="label">Average queue estimate</span></div><div class="kpi"><span class="value">16 min</span><span class="label">Threshold-to-failover delay</span></div></div>
<p>2026年8月8日10:18から10:51まで、Gate Cのファームウェア1.8.2端末でQR_TIMEOUTが増加した。バックアップ切替基準は10:24に成立したが、再起動を優先したため切替は10:40となった。</p>
<h2>2. Timeline</h2>
""" + table(["Time", "Event"], [["10:18", "複数レーンでタイムアウト増加"], ["10:24", "失敗率7%超が5分継続し切替基準成立"], ["10:31", "端末再起動を継続、切替保留"], ["10:40", "SCAN-C-BK1へ切替"], ["10:51", "成功率正常化、待機列解消開始"]]) + """
<h2>3. Cause Classification</h2>
<p><strong>Technical Cause:</strong> Firmware 1.8.2の高輝度QR処理問題。</p>
<p><strong>Operational Cause:</strong> 手順では基準成立から5分以内の切替が必要だが、実際は16分を要した。</p>
<h2>4. Corrective Actions</h2>
""" + bullets(["Gate C全端末を1.9.1へ更新", "Failover判断をNOCとGate Supervisorの共同責任に変更", "閾値成立時の自動通知を追加", "本番前に100件のモバイルウォレット読み取り試験を実施"])
    docs.append({"title": "Gate C 混雑インシデント報告", "subtitle": "QR障害と運用切替遅延", "meta": {"Document ID": "IR-2026-084", "Version": "1.0", "Effective Date": "2026-08-10", **common}, "filename": "IR-2026-084_Gate_C混雑報告", "body": body})

    body = """
<h2>会議情報</h2>
""" + table(["Date", "Topic", "Decision Owner"], [["2026-08-02", "Day 2 Artist Merchandise Inventory", "Merchandise Manager"]]) + """
<h2>1. Lunar Echo Signal Hoodie</h2>
""" + table(["Measure", "Units"], [["Historical baseline", "380"], ["App wishlist forecast", "310"], ["Social mention forecast", "240"], ["Preorder click forecast", "140"], ["Interest-adjusted total forecast", "690"], ["Final planned stock", "420"]]) + """
<h2>2. Discussion</h2>
<p>Digital Commerce担当は、Lunar Echoのヘッドライナー告知後にWishlistとSNS反応が急増しており、少なくとも650着が必要と提案した。物販担当は過年度平均からの増加が大きすぎるとして、420着を維持した。</p>
<div class="callout"><strong>未反映リスク</strong><br>最終決定では、アプリWishlist、SNS Mention、Preorder Clickのシグナルを在庫発注数へ反映しなかった。</div>
<h2>3. Decision</h2>
<p>Day 2の初期在庫を420着とする。追加生産は行わず、完売時は後日受注QRで対応する。</p>
<h2>4. Post-event Note</h2>
<p>実績では2026年8月8日17:40に420着が完売し、在庫切れに関するネガティブフィードバックが250件記録された。次回は関心シグナルを正式な需要予測入力にする。</p>
"""
    docs.append({"title": "物販売上・在庫計画会議 議事録", "subtitle": "Lunar Echo商品需要と在庫決定", "meta": {"Document ID": "MIN-MERCH-2026-04", "Version": "1.0", "Effective Date": "2026-08-02", **common}, "filename": "LSF2026_物販売上在庫計画会議議事録", "body": body})

    body = """
<h2>1. 目的</h2>
<p>AI Agentまたは運営担当者が、分析結果に基づく改善タスクを統制された形で登録するための手順を定める。</p>
<h2>2. 必須項目</h2>
""" + table(["Field", "Required", "Rule"], [["Incident ID", "Yes", "既存インシデントID"], ["Task Title", "Yes", "200文字以内"], ["Description", "Yes", "証拠、原因、完了条件を含む"], ["Priority", "Yes", "LOW / MEDIUM / HIGH / CRITICAL"], ["Owner Team", "Yes", "staff_teamsに存在するTeam ID"], ["Created By Agent", "Yes", "公開済みAgent名"]]) + """
<h2>3. Agent実行ルール</h2>
""" + bullets([
        "Agentは最初に登録案を利用者へ提示する。",
        "利用者の『登録してください』『承認します』などの明示的な承認を確認する。",
        "許可されたCREATE_LSF_IMPROVEMENT_TASKだけを呼び出す。",
        "任意のINSERT、UPDATE、DELETE、無名PL/SQLブロックを生成して実行しない。",
        "成功時は返却されたTask IDを報告し、失敗時は再実行せずエラー内容を提示する。",
    ], ordered=True) + """
<h2>4. Priority例</h2>
""" + table(["Priority", "Example"], [["CRITICAL", "生命安全に直結する未解決リスク"], ["HIGH", "主要ステージ停止の再発防止"], ["MEDIUM", "入場待ち時間や顧客体験の継続的改善"], ["LOW", "表示・説明の改善"]])
    docs.append({"title": "改善タスク登録手順", "subtitle": "Agentによる承認付きアクション", "meta": {"Document ID": "OPS-ACT-1.0", "Version": "1.0", "Effective Date": "2026-07-25", **common}, "filename": "LSF2026_改善タスク登録手順", "body": body})

    return docs


def main() -> None:
    manifest = []
    for doc in documents():
        output = SOURCE_DIR / f"{doc['filename']}.html"
        output.write_text(doc_html(doc), encoding="utf-8")
        manifest.append({"document_id": doc["meta"]["Document ID"], "source": output.name, "pdf": f"{doc['filename']}.pdf"})
    (SOURCE_DIR / "document_build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
