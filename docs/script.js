let rawData = [];
let newsData = [];
let topKData = [];
let cmData = [];
let filteredGlobal = [];

let chartSentFx = null;
let chartShares = null;
let chartProb = null;

const modelMap = {
  rf: {
    label: "Random Forest ganador",
    prob: "prob_up_rf",
    pred: "pred_up_rf",
    signal: "signal_rf",
    hit: "hit_rf"
  },
  var1: {
    label: "Var1 lag_sent_1 + lag_sent_2",
    prob: "prob_up_var1",
    pred: "pred_up_var1",
    signal: "signal_var1",
    hit: "hit_var1"
  },
  baseline: {
    label: "Baseline lag_sent_1",
    prob: "prob_up_baseline",
    pred: "pred_up_baseline",
    signal: "signal_baseline",
    hit: "hit_baseline"
  }
};

Promise.all([
  loadCSV("data/week8_dashboard_data.csv"),
  loadCSV("data/week8_news_by_day.csv"),
  loadCSV("data/week8_topk_configurations.csv"),
  loadCSV("data/week8_confusion_matrix.csv")
]).then(([main, news, topk, cm]) => {
  rawData = main.filter(row => row.date);
  newsData = news.filter(row => row.date);
  topKData = topk;
  cmData = cm;

  initializeDates();
  populateNewsDateSelect();
  updateTopKTable();
  applyFilters();
});

function loadCSV(path) {
  return new Promise(resolve => {
    Papa.parse(path, {
      download: true,
      header: true,
      dynamicTyping: true,
      complete: function(results) {
        resolve(results.data);
      }
    });
  });
}

function initializeDates() {
  const dates = rawData.map(d => d.date).sort();
  document.getElementById("startDate").value = dates[0];
  document.getElementById("endDate").value = dates[dates.length - 1];
}

function populateNewsDateSelect() {
  const select = document.getElementById("newsDateSelect");
  const dates = [...new Set(newsData.map(d => d.date))].sort();

  select.innerHTML = dates.map(d => `<option value="${d}">${d}</option>`).join("");

  const dashboardDates = rawData.map(d => d.date).sort();
  if (dashboardDates.length > 0) {
    select.value = dashboardDates[dashboardDates.length - 1];
  }
}

function getSelectedModel() {
  return modelMap[document.getElementById("modelSelect").value];
}

function applyFilters() {
  const start = document.getElementById("startDate").value;
  const end = document.getElementById("endDate").value;
  const onlyPred = document.getElementById("onlyPredictions").checked;
  const model = getSelectedModel();

  let filtered = rawData.filter(row => row.date >= start && row.date <= end);

  if (onlyPred) {
    filtered = filtered.filter(row => hasPrediction(row, model));
  }

  filteredGlobal = filtered;

  updateKPIs(filtered, model);
  updateCharts(filtered, model);
  updateTable(filtered, model);
  updateTrafficLights(filtered, model);
  updateRanking(filtered);
  updateConfusionMatrix(filtered, model);
}

function hasPrediction(row, model) {
  return row[model.pred] !== null && row[model.pred] !== "" && row[model.pred] !== undefined;
}

function toBool(value) {
  return value === true || value === "true" || value === "True" || value === 1 || value === "1";
}

function mean(arr) {
  const clean = arr.filter(x => x !== null && x !== undefined && !isNaN(x));
  if (clean.length === 0) return null;
  return clean.reduce((a, b) => a + b, 0) / clean.length;
}

function sum(arr) {
  return arr.filter(x => !isNaN(x)).reduce((a, b) => a + b, 0);
}

function updateKPIs(data, model) {
  const totalNews = sum(data.map(d => Number(d.n_news_total || 0)));
  const avgSent = mean(data.map(d => Number(d.sent_index_mean)));

  const firstClose = Number(data[0]?.close);
  const lastClose = Number(data[data.length - 1]?.close);
  const fxChange = (!isNaN(firstClose) && !isNaN(lastClose)) ? lastClose - firstClose : null;

  const validPreds = data.filter(d => hasPrediction(d, model));
  const hits = validPreds.filter(d => toBool(d[model.hit]));
  const hitRate = validPreds.length > 0 ? hits.length / validPreds.length : null;

  document.getElementById("kpiNews").textContent = totalNews.toFixed(0);
  document.getElementById("kpiSent").textContent = avgSent !== null ? avgSent.toFixed(3) : "-";
  document.getElementById("kpiFx").textContent = fxChange !== null ? fxChange.toFixed(4) : "-";
  document.getElementById("kpiHit").textContent = hitRate !== null ? (hitRate * 100).toFixed(1) + "%" : "-";
}

function updateCharts(data, model) {
  const labels = data.map(d => d.date);

  const sent = data.map(d => Number(d.sent_index_mean));
  const close = data.map(d => Number(d.close));
  const sharePos = data.map(d => Number(d.share_pos));
  const shareNeg = data.map(d => Number(d.share_neg));
  const shareNeu = data.map(d => Number(d.share_neu));
  const probUp = data.map(d => hasPrediction(d, model) ? Number(d[model.prob]) : null);

  if (chartSentFx) chartSentFx.destroy();
  if (chartShares) chartShares.destroy();
  if (chartProb) chartProb.destroy();

  chartSentFx = new Chart(document.getElementById("chartSentFx"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: "Sentimiento promedio", data: sent, yAxisID: "y", borderWidth: 2 },
        { label: "USD/PEN Close", data: close, yAxisID: "y1", borderWidth: 2 }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { type: "linear", position: "left" },
        y1: { type: "linear", position: "right", grid: { drawOnChartArea: false } }
      }
    }
  });

  chartShares = new Chart(document.getElementById("chartShares"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: "Share positivo", data: sharePos, borderWidth: 2 },
        { label: "Share negativo", data: shareNeg, borderWidth: 2 },
        { label: "Share neutral", data: shareNeu, borderWidth: 2 }
      ]
    },
    options: {
      responsive: true,
      scales: { y: { min: 0, max: 1 } }
    }
  });

  chartProb = new Chart(document.getElementById("chartProb"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: `Probabilidad UP - ${model.label}`, data: probUp, borderWidth: 2, spanGaps: true },
        { label: "Umbral 0.50", data: labels.map(() => 0.5), borderWidth: 1, borderDash: [5, 5], pointRadius: 0 }
      ]
    },
    options: {
      responsive: true,
      scales: { y: { min: 0, max: 1 } }
    }
  });
}

function updateTrafficLights(data, model) {
  const div = document.getElementById("trafficLights");

  div.innerHTML = data.map(row => {
    let cls = "neutral";
    let txt = "Sin predicción";

    if (hasPrediction(row, model)) {
      if (toBool(row[model.hit])) {
        cls = "success";
        txt = "Acierto";
      } else {
        cls = "error";
        txt = "Error";
      }
    }

    return `
      <div class="traffic-item ${cls}" title="${row.date} | ${txt}">
        <span>${row.date}</span>
      </div>
    `;
  }).join("");
}

function updateRanking(data) {
  const ranked = [...data]
    .filter(d => !isNaN(Number(d.sent_index_mean)))
    .sort((a, b) => Math.abs(Number(b.sent_index_mean)) - Math.abs(Number(a.sent_index_mean)))
    .slice(0, 10);

  const div = document.getElementById("rankingSentiment");

  div.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Ranking</th>
          <th>Fecha</th>
          <th>Sentimiento</th>
          <th>Noticias</th>
          <th>Real USD/PEN</th>
        </tr>
      </thead>
      <tbody>
        ${ranked.map((d, i) => `
          <tr>
            <td>${i + 1}</td>
            <td>${d.date}</td>
            <td>${Number(d.sent_index_mean).toFixed(4)}</td>
            <td>${d.n_news_total}</td>
            <td>${d.real_dir}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function updateTopNews() {
  const date = document.getElementById("newsDateSelect").value;

  const rows = newsData
    .filter(d => d.date === date)
    .sort((a, b) => Number(b.sentiment_score_abs || 0) - Number(a.sentiment_score_abs || 0))
    .slice(0, 8);

  const div = document.getElementById("topNews");

  if (rows.length === 0) {
    div.innerHTML = "<p>No hay noticias para esta fecha.</p>";
    return;
  }

  div.innerHTML = rows.map(n => `
    <div class="news-card">
      <h4>${n.title_raw || "Sin título"}</h4>
      <p><strong>Fuente:</strong> ${n.source || "-"}</p>
      <p><strong>Sentimiento:</strong> ${n.sentiment_label || "-"} |
      Pos: ${formatNum(n.p_pos)} Neu: ${formatNum(n.p_neu)} Neg: ${formatNum(n.p_neg)}</p>
      ${n.url ? `<a href="${n.url}" target="_blank">Ver noticia</a>` : ""}
    </div>
  `).join("");
}

function formatNum(x) {
  const n = Number(x);
  return isNaN(n) ? "-" : n.toFixed(3);
}

function toggleModelExplanation() {
  document.getElementById("modelExplanation").classList.toggle("hidden");
}

function updateTopKTable() {
  const columns = ["global_rank", "model_family", "mean_test_score", "std_test_score", "mean_fit_time", "params"];

  const thead = document.querySelector("#topKTable thead");
  const tbody = document.querySelector("#topKTable tbody");

  thead.innerHTML = "<tr>" + columns.map(c => `<th>${c}</th>`).join("") + "</tr>";

  tbody.innerHTML = topKData.slice(0, 10).map(row => {
    return "<tr>" + columns.map(c => {
      let val = row[c];
      if (typeof val === "number") val = val.toFixed(4);
      if (val === null || val === undefined) val = "";
      return `<td>${val}</td>`;
    }).join("") + "</tr>";
  }).join("");
}

function updateConfusionMatrix(data, model) {
  document.getElementById("cmModelName").textContent = model.label;

  let tn = 0, fp = 0, fn = 0, tp = 0;

  data.filter(d => hasPrediction(d, model)).forEach(d => {
    const real = Number(d.target_up);
    const pred = Number(d[model.pred]);

    if (real === 0 && pred === 0) tn++;
    if (real === 0 && pred === 1) fp++;
    if (real === 1 && pred === 0) fn++;
    if (real === 1 && pred === 1) tp++;
  });

  const div = document.getElementById("confusionMatrix");

  div.innerHTML = `
    <div></div>
    <div class="cm-header">Pred NO_UP</div>
    <div class="cm-header">Pred UP</div>

    <div class="cm-header">Real NO_UP</div>
    <div class="cm-cell good">${tn}</div>
    <div class="cm-cell bad">${fp}</div>

    <div class="cm-header">Real UP</div>
    <div class="cm-cell bad">${fn}</div>
    <div class="cm-cell good">${tp}</div>
  `;
}

function updateTable(data, model) {
  const columns = [
    "date",
    "n_news_total",
    "sent_index_mean",
    "share_pos",
    "share_neg",
    "share_neu",
    "close",
    "real_dir",
    model.prob,
    model.signal,
    model.hit
  ];

  const thead = document.querySelector("#dataTable thead");
  const tbody = document.querySelector("#dataTable tbody");

  thead.innerHTML = "<tr>" + columns.map(c => `<th>${c}</th>`).join("") + "</tr>";

  tbody.innerHTML = data.map(row => {
    return "<tr>" + columns.map(c => {
      let val = row[c];
      if (typeof val === "number") val = val.toFixed(4);
      if (val === null || val === undefined) val = "";
      return `<td>${val}</td>`;
    }).join("") + "</tr>";
  }).join("");
}

function downloadFilteredCSV() {
  const model = getSelectedModel();

  const columns = [
    "date",
    "n_news_total",
    "sent_index_mean",
    "share_pos",
    "share_neg",
    "share_neu",
    "open",
    "close",
    "fx_diff",
    "fx_return",
    "real_dir",
    "target_up",
    model.prob,
    model.pred,
    model.signal,
    model.hit
  ];

  const rows = filteredGlobal.map(row => {
    return columns.map(c => `"${row[c] ?? ""}"`).join(",");
  });

  const csv = [columns.join(","), ...rows].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "dashboard_filtrado.csv";
  a.click();

  URL.revokeObjectURL(url);
}