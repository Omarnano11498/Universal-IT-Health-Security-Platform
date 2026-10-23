from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.scanner import run_scan

app = FastAPI(title="Universal IT Health & Security")
LATEST_SCAN_RESULTS = None

DASHBOARD = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>صحة وأمان تقنية المعلومات</title>
  <style>
    :root { color-scheme: light; font: 16px/1.6 system-ui, sans-serif; color: #172033; background: #f3f6fb; }
    * { box-sizing: border-box; }
    body { margin: 0; }
    header { background: #12243a; color: white; padding: 24px max(20px, calc((100% - 1100px)/2)); }
    header h1 { margin: 0 0 4px; font-size: 1.6rem; }
    main { max-width: 1100px; margin: 24px auto; padding: 0 18px 40px; }
    .toolbar, .panel { background: white; border: 1px solid #e0e6ef; border-radius: 12px; padding: 18px; margin-bottom: 18px; }
    .toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
    button, select, input { font: inherit; border-radius: 8px; padding: 9px 12px; }
    button { border: 0; color: white; background: #1769aa; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    select, input { border: 1px solid #bdc8d8; background: white; }
    #message { min-height: 1.6em; color: #42536a; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 12px; }
    .metric { background: #f5f8fc; padding: 14px; border-radius: 9px; }
    .metric strong { display: block; font-size: 1.35rem; }
    .finding { border: 1px solid #e0e6ef; border-inline-start: 4px solid #70839b; border-radius: 8px; padding: 12px; margin: 10px 0; }
    .finding[data-severity="MEDIUM"], .finding[data-severity="HIGH"], .finding[data-severity="CRITICAL"] { border-inline-start-color: #c75a24; }
    .finding h3 { margin: 0; font-size: 1.05rem; }
    .muted { color: #596a80; }
    .table-wrap { overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { padding: 8px; border-bottom: 1px solid #e0e6ef; text-align: start; }
    [hidden] { display: none !important; }
    @media (max-width: 600px) { header { padding: 20px; } main { margin-top: 14px; } }
  </style>
</head>
<body>
  <header>
    <h1 data-i18n="title">صحة وأمان تقنية المعلومات</h1>
    <div data-i18n="subtitle">فحص محلي للقراءة فقط — لا يتم فحص أجهزة أخرى أو تنفيذ إصلاحات.</div>
  </header>
  <main>
    <section class="toolbar" aria-label="أدوات الفحص">
      <button id="run-scan" type="button" data-i18n="run">ابدأ الفحص المحلي</button>
      <button id="refresh" type="button" data-i18n="refresh">تحديث النتائج</button>
      <button id="download" type="button" disabled data-i18n="download">تنزيل JSON</button>
      <label for="lang" data-i18n="language-label">اللغة</label>
      <select id="lang" aria-label="Language">
        <option value="ar" selected>العربية</option><option value="en">English</option>
      </select>
      <label for="filter" data-i18n="filter-label">تصفية النتائج</label>
      <input id="filter" type="search" data-i18n-placeholder="filter-placeholder" placeholder="ابحث في النتائج">
    </section>
    <p id="message" role="status" aria-live="polite" data-i18n="ready">جاهز. ابدأ الفحص لجمع بيانات الجهاز.</p>
    <section id="results" hidden>
      <section class="panel">
        <h2 data-i18n="summary">ملخص الفحص</h2>
        <div id="summary" class="grid"></div>
        <p id="scan-meta" class="muted"></p>
      </section>
      <section class="panel">
        <h2 data-i18n="findings">النتائج والتوصيات</h2>
        <div id="findings"></div>
      </section>
      <section class="panel">
        <h2 data-i18n="device">معلومات الجهاز</h2>
        <div id="device-info" class="grid"></div>
      </section>
      <section class="panel">
        <h2 data-i18n="health">صحة النظام</h2>
        <div id="health-info" class="grid"></div>
      </section>
      <section class="panel">
        <h2 data-i18n="network">واجهات الشبكة والمنافذ المستمعة</h2>
        <div id="network-info"></div>
      </section>
    </section>
  </main>
  <script>
    const words = {
      ar: {title:"صحة وأمان تقنية المعلومات",subtitle:"فحص محلي للقراءة فقط — لا يتم فحص أجهزة أخرى أو تنفيذ إصلاحات.",
        run:"ابدأ الفحص المحلي",running:"جارٍ جمع بيانات الجهاز...",refresh:"تحديث النتائج",download:"تنزيل JSON",
        "language-label":"اللغة","filter-label":"تصفية النتائج","filter-placeholder":"ابحث في النتائج",
        ready:"جاهز. ابدأ الفحص لجمع بيانات الجهاز.",summary:"ملخص الفحص",findings:"النتائج والتوصيات",
        device:"معلومات الجهاز",health:"صحة النظام",network:"واجهات الشبكة والمنافذ المستمعة",
        noPrevious:"لا توجد نتائج محفوظة بعد. ابدأ الفحص.",scanDone:"اكتمل الفحص المحلي.",
        scanError:"تعذر إكمال الفحص: ",refreshError:"تعذر تحميل النتائج: ",noMatches:"لا توجد نتائج مطابقة.",
        scanId:"معرّف الفحص",scope:"النطاق",timestamp:"الوقت",total:"إجمالي النتائج",critical:"حرج",
        high:"مرتفع",medium:"متوسط",info:"معلومات",hostname:"اسم الجهاز",system:"النظام",
        release:"الإصدار",architecture:"المعمارية",admin:"صلاحية مسؤول",yes:"نعم",no:"لا",
        cpu:"استخدام المعالج",memory:"استخدام الذاكرة",processes:"عدد العمليات",disks:"الأقراص",
        interfaces:"واجهات الشبكة",listeners:"المنافذ المستمعة",status:"الحالة",recommendation:"التوصية",
        mount:"نقطة الربط",percent:"الاستخدام",address:"العنوان",port:"المنفذ",noData:"لا توجد بيانات متاحة",
        collected:"تم الجمع",skipped:"تم التخطي",limited:"النطاق محدود",measured:"تم القياس"},
      en: {title:"IT Health & Security",subtitle:"Read-only local scan — no other devices are scanned and no fixes are executed.",
        run:"Run local scan",running:"Collecting device data...",refresh:"Refresh results",download:"Download JSON",
        "language-label":"Language","filter-label":"Filter results","filter-placeholder":"Search results",
        ready:"Ready. Start a scan to collect device data.",summary:"Scan summary",findings:"Findings & recommendations",
        device:"Device information",health:"System health",network:"Network interfaces & listening ports",
        noPrevious:"No saved results yet. Start a scan.",scanDone:"Local scan completed.",
        scanError:"Could not complete the scan: ",refreshError:"Could not load results: ",noMatches:"No matching results.",
        scanId:"Scan ID",scope:"Scope",timestamp:"Time",total:"Total findings",critical:"Critical",
        high:"High",medium:"Medium",info:"Info",hostname:"Hostname",system:"System",
        release:"Release",architecture:"Architecture",admin:"Administrator",yes:"Yes",no:"No",
        cpu:"CPU utilization",memory:"Memory utilization",processes:"Process count",disks:"Disks",
        interfaces:"Network interfaces",listeners:"Listening ports",status:"Status",recommendation:"Recommendation",
        mount:"Mount point",percent:"Usage",address:"Address",port:"Port",noData:"No data available",
        collected:"Collected",skipped:"Skipped",limited:"Limited scope",measured:"Measured"}
    };
    let language = "ar";
    let currentScan = null;
    const $ = (id) => document.getElementById(id);
    const t = (key) => words[language][key] || key;
    function addCard(parent, label, value) {
      const card = document.createElement("div");
      card.className = "metric";
      const name = document.createElement("span");
      name.textContent = label;
      const val = document.createElement("strong");
      val.textContent = value === null || value === undefined || value === "" ? "—" : String(value);
      card.append(name, val);
      parent.append(card);
    }
    function applyLanguage() {
      document.documentElement.lang = language;
      document.documentElement.dir = language === "ar" ? "rtl" : "ltr";
      document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
      document.querySelectorAll("[data-i18n-placeholder]").forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
      if (currentScan) render(currentScan);
    }
    function render(scan) {
      currentScan = scan;
      $("results").hidden = false;
      $("download").disabled = false;
      $("summary").replaceChildren();
      const summary = scan.summary || {};
      [["total","total_findings"],["critical","critical"],["high","high"],["medium","medium"],["info","info"]]
        .forEach(([label,key]) => addCard($("summary"), t(label), summary[key] ?? 0));
      $("scan-meta").textContent = `${t("scanId")}: ${scan.scan_id || "—"} · ${t("scope")}: ${scan.scope || "—"} · ${t("timestamp")}: ${scan.timestamp || "—"}`;

      const findings = $("findings");
      findings.replaceChildren();
      const query = $("filter").value.trim().toLocaleLowerCase();
      const matching = (scan.findings || []).filter(item =>
        `${item.title || ""} ${item.recommendation || ""} ${item.mountpoint || ""}`.toLocaleLowerCase().includes(query));
      if (!matching.length) findings.textContent = t("noMatches");
      matching.forEach(item => {
        const card = document.createElement("article");
        card.className = "finding";
        card.dataset.severity = item.severity || "";
        const title = document.createElement("h3");
        title.textContent = `${item.title || t("noData")} · ${item.severity || "—"}`;
        const note = document.createElement("p");
        note.textContent = `${t("recommendation")}: ${item.recommendation || "—"}${item.mountpoint ? ` (${item.mountpoint})` : ""}`;
        card.append(title, note);
        findings.append(card);
      });

      const info = scan.system_info || {};
      $("device-info").replaceChildren();
      if (info.status) addCard($("device-info"), t("status"), `${info.status}${info.reason ? ` — ${info.reason}` : ""}`);
      [["hostname",info.hostname],["system",info.system],["release",info.release],
        ["architecture",info.machine],["admin",info.is_admin === undefined ? "—" : t(info.is_admin ? "yes" : "no")]]
        .forEach(([label,value]) => addCard($("device-info"), t(label), value));

      const health = scan.health || {};
      const cpu = health.cpu || {};
      const memory = health.memory || {};
      $("health-info").replaceChildren();
      addCard($("health-info"), t("cpu"), cpu.cpu_percent_sample === undefined ? "—" : `${cpu.cpu_percent_sample}%`);
      addCard($("health-info"), t("memory"), memory.percent_used === undefined ? "—" : `${memory.percent_used}%`);
      addCard($("health-info"), t("processes"), health.process_count);
      if (health.status) addCard($("health-info"), t("status"), `${health.status}${health.reason ? ` — ${health.reason}` : ""}`);
      const disks = health.disks || [];
      disks.forEach(disk => addCard($("health-info"), `${t("disks")}: ${disk.mountpoint || disk.device || "—"}`,
        disk.percent_used === undefined ? (disk.reason || disk.status || "—") : `${disk.percent_used}%`));
      if (!health.status && !health.memory && !disks.length) addCard($("health-info"), t("status"), t("noData"));

      const network = scan.network || {};
      const networkPanel = $("network-info");
      networkPanel.replaceChildren();
      const interfaces = network.interfaces || {};
      if (network.status) {
        const error = document.createElement("p");
        error.textContent = `${network.status}${network.reason ? ` — ${network.reason}` : ""}`;
        networkPanel.append(error);
      }
      Object.entries(interfaces).forEach(([name, addresses]) => {
        const row = document.createElement("p");
        row.textContent = `${t("interfaces")}: ${name} — ${(addresses || []).map(item => item.address).filter(Boolean).join(", ") || "—"}`;
        networkPanel.append(row);
      });
      const listeners = network.listeners || [];
      if (listeners.length) {
        const tableWrap = document.createElement("div");
        tableWrap.className = "table-wrap";
        const table = document.createElement("table");
        const header = document.createElement("tr");
        [t("status"),t("address"),t("port")].forEach(label => {
          const th = document.createElement("th"); th.textContent = label; header.append(th);
        });
        table.append(header);
        listeners.forEach(item => {
          const row = document.createElement("tr");
          [item.type || item.status || "—",item.local_address || "—",item.local_port || "—"].forEach(value => {
            const cell = document.createElement("td"); cell.textContent = String(value); row.append(cell);
          });
          table.append(row);
        });
        tableWrap.append(table);
        networkPanel.append(tableWrap);
      }
      if (!networkPanel.childElementCount) networkPanel.textContent = network.listeners_reason || t("noData");
    }
    async function loadLatest() {
      $("message").textContent = t("running");
      try {
        const response = await fetch("/api/scan/results");
        if (response.status === 404) { $("message").textContent = t("noPrevious"); return; }
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
        const result = await response.json();
        render(result.data);
        $("message").textContent = t("scanDone");
      } catch (error) {
        $("message").textContent = t("refreshError") + error.message;
      }
    }
    $("run-scan").addEventListener("click", async () => {
      const button = $("run-scan");
      button.disabled = true;
      $("message").textContent = t("running");
      try {
        const response = await fetch("/api/scan", {method:"POST"});
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || response.statusText);
        render(result.data);
        $("message").textContent = t("scanDone");
      } catch (error) {
        $("message").textContent = t("scanError") + error.message;
      } finally {
        button.disabled = false;
      }
    });
    $("refresh").addEventListener("click", loadLatest);
    $("filter").addEventListener("input", () => { if (currentScan) render(currentScan); });
    $("lang").addEventListener("change", event => { language = event.target.value; applyLanguage(); });
    $("download").addEventListener("click", () => {
      if (!currentScan) return;
      const blob = new Blob([JSON.stringify(currentScan, null, 2)], {type:"application/json"});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `scan-${currentScan.scan_id || "latest"}.json`;
      link.click();
      URL.revokeObjectURL(link.href);
    });
    loadLatest();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/scan")
def start_scan():
    global LATEST_SCAN_RESULTS
    LATEST_SCAN_RESULTS = run_scan()
    return {"success": True, "data": LATEST_SCAN_RESULTS}


@app.get("/api/scan/results")
def get_scan_results():
    if LATEST_SCAN_RESULTS is None:
        raise HTTPException(status_code=404, detail="No scan results are available yet.")
    return {"success": True, "data": LATEST_SCAN_RESULTS}


@app.post("/api/scans")
def receive_scan(scan: dict):
    global LATEST_SCAN_RESULTS
    if not scan.get("scan_id"):
        raise HTTPException(status_code=422, detail="scan_id is required.")
    LATEST_SCAN_RESULTS = scan
    return {"success": True, "scan_id": scan["scan_id"]}
