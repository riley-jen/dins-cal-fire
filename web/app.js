const fires = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge'];
const damageList = [
  'no damage',
  'affected (>0-10%)',
  'minor (10-25%)',
  'major (25-50%)',
  'destroyed (>50%)',
  'inaccessible',
];
const damageColors = {
  'no damage': 'green',
  'affected (>0-10%)': 'gold',
  'minor (10-25%)': 'orange',
  'major (25-50%)': 'red',
  'destroyed (>50%)': 'black',
  inaccessible: 'gray',
};
const materials = ['asphalt', 'composite', 'masonry', 'metal', 'tile', 'vinyl', 'wood', 'n/a'];
const buildingElements = ['ROOFCONSTRUCTION', 'EXTERIORSIDING', 'DECKPORCHONGRADE', 'DECKPORCHELEVATED'];
const buildingElementLabels = ['material', 'roof', 'side', 'ground deck', 'elevated deck'];
const materialColors = {
  wood: '#8B4513',
  asphalt: '#333333',
  vinyl: '#F4E1A6',
  composite: '#D2691E',
  metal: '#708090',
  masonry: '#B22222',
  tile: '#4682B4',
  'n/a': '#D3D3D3',
};
const combustibleMaterials = ['asphalt', 'composite', 'vinyl', 'wood'];
const nonCombustibleMaterials = ['masonry', 'metal', 'tile'];
const samplingTypes = ['Chips', 'Sorbent Tubes', 'Wipes', 'Wristbands'];
const samplingColors = {
  Chips: '#54d3a9',
  'Sorbent Tubes': '#F28E2B',
  Wipes: '#2F80ED',
  Wristbands: '#E85D9E',
};
const samplingData = {
  bridge: [
    ['2024-09-10', ['Wipes']],
    ['2024-09-11', ['Chips', 'Sorbent Tubes', 'Wristbands']],
    ['2024-09-12', ['Sorbent Tubes', 'Wipes', 'Wristbands']],
    ['2024-09-13', ['Chips']],
    ['2024-09-14', ['Chips', 'Sorbent Tubes', 'Wipes', 'Wristbands']],
  ],
  line: [
    ['2024-09-10', ['Chips', 'Sorbent Tubes', 'Wristbands']],
    ['2024-09-12', ['Wristbands']],
    ['2024-09-13', ['Chips']],
  ],
  franklin: [['2024-12-10', ['Chips', 'Wipes', 'Wristbands']]],
  eaton: [['2025-01-08', ['Wristbands']]],
  mountain: [['2024-11-07', ['Wipes']]],
  palisades: [['2025-01-11', ['Wristbands']]],
};
const structureConfigs = [
  {
    key: 'eaves-table',
    columns: ['build', 'eaves'],
    properties: ['EAVES'],
    rows: ['enclosed', 'unenclosed', 'n/a'],
    rowMap: {
      enclosed: 'enclosed',
      unenclosed: 'unenclosed',
      'no eaves': 'n/a',
      unknown: 'n/a',
    },
  },
  {
    key: 'ventscreen-table',
    columns: ['build', 'mesh screen'],
    properties: ['VENTSCREEN'],
    rows: ['<= 1/8"', '> 1/8"', 'unscreened', 'n/a'],
    rowMap: {
      'mesh screen <= 1/8"': '<= 1/8"',
      'mesh screen > 1/8"': '> 1/8"',
      unscreened: 'unscreened',
      'no vents': 'n/a',
      unknown: 'n/a',
    },
  },
  {
    key: 'windowpane-table',
    columns: ['build', 'window pane'],
    properties: ['WINDOWPANE'],
    rows: ['single pane', 'multi pane', 'n/a'],
    rowMap: {
      'single pane': 'single pane',
      'multi pane': 'multi pane',
      'no windows': 'n/a',
      unknown: 'n/a',
    },
  },
];
const combustibilityConfig = {
  columns: ['combustibility', 'roof', 'side', 'ground deck', 'elevated deck', 'patio cover', 'fence'],
  properties: ['PATIOCOVERCARPORT', 'FENCEATTACHEDTOSTRUCTURE'],
  rows: ['combustible', 'non-combustible', 'n/a'],
  rowMap: {
    combustible: 'combustible',
    'non combustible': 'non-combustible',
    'non-combustible': 'non-combustible',
    'no patio cover carport': 'n/a',
    'no patio cover/carport': 'n/a',
    'no fence': 'n/a',
    unknown: 'n/a',
  },
};

let map;
let structureLayer;
let perimeterLayer;
let damageChart;
let samplingChart;
let materialChart;
let structureFeatures = [];
let perimeterFeatures = [];
let currentFire = 'palisades';
let displayedDamages = [...damageList];

function cleanValue(value) {
  return String(value ?? '').trim().toLowerCase();
}

function getMaterial(value) {
  const clean = cleanValue(value).replace('/', ' ');

  if (materials.includes(clean)) {
    return clean;
  }

  if (['masonry concrete', 'stucco brick cement', 'concrete'].includes(clean)) {
    return 'masonry';
  }

  if (clean.includes('no ') || clean.includes('other') || clean.includes('unknown')) {
    return 'n/a';
  }

  return 'n/a';
}

function getRoundedPercentages(counts) {
  const total = counts.reduce((sum, count) => sum + count, 0);
  if (total === 0) {
    return counts.map(() => 0);
  }

  const exact = counts.map((count) => (count / total) * 100);
  const rounded = exact.map((percent) => Math.floor(percent));
  let remainder = 100 - rounded.reduce((sum, count) => sum + count, 0);
  const order = counts
    .map((_, index) => index)
    .sort((a, b) => (exact[b] - rounded[b]) - (exact[a] - rounded[a]));

  for (const index of order.slice(0, remainder)) {
    rounded[index] += 1;
  }

  return rounded;
}

function formatCountPercentRows(rows, columns) {
  const formatted = rows.map((row) => ({ ...row }));

  for (const column of columns.slice(1)) {
    const counts = formatted.map((row) => row[column]);
    const percentages = getRoundedPercentages(counts);
    formatted.forEach((row, index) => {
      row[column] = `${counts[index]} (${percentages[index]}%)`;
    });
  }

  return formatted;
}

function renderTable(hostId, columns, rows) {
  const host = document.getElementById(hostId);
  const header = columns.map((column) => `<th>${column}</th>`).join('');
  const body = rows
    .map((row) => `<tr>${columns.map((column) => `<td>${row[column]}</td>`).join('')}</tr>`)
    .join('');

  host.innerHTML = `<table><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table>`;
}

function getFireFeatures() {
  return structureFeatures.filter((feature) => cleanValue(feature.properties.INCIDENTNAME) === currentFire);
}

function getDisplayedFeatures() {
  return getFireFeatures().filter((feature) => displayedDamages.includes(cleanValue(feature.properties.DAMAGE)));
}

function getDamageCounts(features) {
  const counts = Object.fromEntries(damageList.map((damage) => [damage, 0]));

  for (const feature of features) {
    const damage = cleanValue(feature.properties.DAMAGE);
    if (damage in counts) {
      counts[damage] += 1;
    }
  }

  return counts;
}

function getMaterialRows(features) {
  const rows = materials.map((material) => {
    const row = { material };
    for (const label of buildingElementLabels.slice(1)) {
      row[label] = 0;
    }
    return row;
  });

  for (const [index, property] of buildingElements.entries()) {
    const label = buildingElementLabels[index + 1];
    for (const feature of features) {
      const material = getMaterial(feature.properties[property]);
      rows.find((row) => row.material === material)[label] += 1;
    }
  }

  return formatCountPercentRows(rows, buildingElementLabels);
}

function getCellPercent(value) {
  const match = String(value).match(/\((\d+)%\)/);
  return match ? Number(match[1]) : 0;
}

function getStructureRow(value, config) {
  const clean = cleanValue(value);
  if (clean in config.rowMap) {
    return config.rowMap[clean];
  }

  const withoutSlash = clean.replace('/', ' ');
  if (withoutSlash in config.rowMap) {
    return config.rowMap[withoutSlash];
  }

  return 'n/a';
}

function getStructureRows(features, config) {
  const rows = config.rows.map((rowName) => {
    const row = { [config.columns[0]]: rowName };
    for (const column of config.columns.slice(1)) {
      row[column] = 0;
    }
    return row;
  });

  for (const [index, property] of config.properties.entries()) {
    const column = config.columns[index + 1];
    for (const feature of features) {
      const rowName = getStructureRow(feature.properties[property], config);
      rows.find((row) => row[config.columns[0]] === rowName)[column] += 1;
    }
  }

  return formatCountPercentRows(rows, config.columns);
}

function getMaterialCombustibilityCounts(features, property) {
  const counts = {
    combustible: 0,
    'non-combustible': 0,
    'n/a': 0,
  };

  for (const feature of features) {
    const raw = cleanValue(feature.properties[property]);
    const material = getMaterial(feature.properties[property]);

    if (raw === 'combustible' || combustibleMaterials.includes(material)) {
      counts.combustible += 1;
    } else if (['non combustible', 'non-combustible'].includes(raw) || nonCombustibleMaterials.includes(material)) {
      counts['non-combustible'] += 1;
    } else {
      counts['n/a'] += 1;
    }
  }

  return counts;
}

function getCombustibilityRows(features) {
  const tableValues = buildingElements.map((property) => getMaterialCombustibilityCounts(features, property));

  for (const property of combustibilityConfig.properties) {
    const counts = Object.fromEntries(combustibilityConfig.rows.map((row) => [row, 0]));
    for (const feature of features) {
      counts[getStructureRow(feature.properties[property], combustibilityConfig)] += 1;
    }
    tableValues.push(counts);
  }

  const rows = combustibilityConfig.rows.map((rowName) => {
    const row = { combustibility: rowName };
    combustibilityConfig.columns.slice(1).forEach((column, index) => {
      row[column] = tableValues[index][rowName];
    });
    return row;
  });

  return formatCountPercentRows(rows, combustibilityConfig.columns);
}

function initMap() {
  map = L.map('map', {
    zoomControl: false,
    renderer: L.canvas(),
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap',
  }).addTo(map);
}

function updateMap() {
  if (structureLayer) {
    structureLayer.remove();
  }
  if (perimeterLayer) {
    perimeterLayer.remove();
  }

  const displayed = getDisplayedFeatures();
  structureLayer = L.geoJSON(displayed, {
    pointToLayer(feature, latlng) {
      const damage = cleanValue(feature.properties.DAMAGE);
      return L.circleMarker(latlng, {
        radius: 2,
        stroke: false,
        fillColor: damageColors[damage],
        fillOpacity: 0.8,
      });
    },
  }).addTo(map);

  perimeterLayer = L.geoJSON(
    perimeterFeatures.filter((feature) => cleanValue(feature.properties.poly_IncidentName) === currentFire),
    {
      style: {
        color: 'blue',
        fillColor: 'blue',
        fillOpacity: 0.3,
        opacity: 0.6,
        weight: 1,
      },
    },
  ).addTo(map);

  const bounds = L.featureGroup([structureLayer, perimeterLayer]).getBounds();
  if (bounds.isValid()) {
    map.fitBounds(bounds.pad(0.08), { animate: false });
  }
}

function updateDamageChart() {
  const allFeatures = getFireFeatures();
  const counts = getDamageCounts(allFeatures);
  const visibleCounts = damageList.map((damage) => (displayedDamages.includes(damage) ? counts[damage] : 0));
  const total = visibleCounts.reduce((sum, count) => sum + count, 0);
  const fireTotal = allFeatures.length;

  damageChart.data.datasets[0].data = visibleCounts;
  damageChart.update();

  const percentages = getRoundedPercentages(visibleCounts);
  const rows = damageList
    .map((damage, index) => {
      const count = visibleCounts[index];
      return `
        <div class="legend-row">
          <span class="legend-swatch" style="background:${damageColors[damage]}"></span>
          <span>${count} (${percentages[index]}%)</span>
        </div>
      `;
    })
    .join('');
  const displayedPercent = fireTotal ? Math.round((total / fireTotal) * 100) : 0;
  document.getElementById('damage-legend').innerHTML = `
    <div class="legend-title">displayed: ${total} (${displayedPercent}%)</div>
    ${rows}
  `;
}

function initCharts() {
  damageChart = new Chart(document.getElementById('damage-chart'), {
    type: 'pie',
    data: {
      labels: damageList,
      datasets: [{
        data: damageList.map(() => 0),
        backgroundColor: damageList.map((damage) => damageColors[damage]),
        borderWidth: 0,
      }],
    },
    options: {
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
    },
  });

  samplingChart = new Chart(document.getElementById('sampling-chart'), {
    type: 'scatter',
    data: { datasets: [] },
    options: {
      animation: false,
      maintainAspectRatio: false,
      scales: {
        x: {
          min: -0.5,
          max: 0.5,
          grid: { color: '#d9d9d9' },
          ticks: { callback: () => '' },
        },
        y: {
          min: -0.5,
          max: samplingTypes.length - 0.5,
          grid: { color: '#d9d9d9' },
          ticks: {
            stepSize: 1,
            callback(value) {
              return [...samplingTypes].reverse()[value] || '';
            },
          },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });

  materialChart = new Chart(document.getElementById('material-chart'), {
    type: 'bar',
    data: {
      labels: ['roof', 'side', 'ground deck', 'elevated deck'],
      datasets: [],
    },
    options: {
      indexAxis: 'y',
      animation: false,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          min: 0,
          max: 100,
          display: false,
        },
        y: {
          stacked: true,
          grid: { display: false },
        },
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            font: { size: 9 },
          },
        },
        tooltip: { enabled: false },
      },
    },
  });
}

function updateSamplingChart() {
  const data = samplingData[currentFire] || [];
  const dates = data.map(([date]) => date);
  const datePositions = Object.fromEntries(dates.map((date, index) => [date, index]));
  const typePositions = Object.fromEntries(samplingTypes.map((type, index) => [type, samplingTypes.length - index - 1]));

  samplingChart.data.datasets = samplingTypes.map((type) => ({
    label: type,
    data: data
      .filter(([, types]) => types.includes(type))
      .map(([date]) => ({ x: datePositions[date], y: typePositions[type] })),
    pointRadius: 5,
    pointBackgroundColor: samplingColors[type],
    pointBorderColor: '#ffffff',
    pointBorderWidth: 1,
  }));
  samplingChart.options.scales.x.max = Math.max(dates.length - 0.5, 0.5);
  samplingChart.options.scales.x.ticks.callback = (value) => dates[value] || '';
  samplingChart.update();
}

function updateMaterialChart(materialRows) {
  materialChart.data.datasets = materials.map((material) => {
    const row = materialRows.find((candidate) => candidate.material === material);
    return {
      label: material,
      data: ['roof', 'side', 'ground deck', 'elevated deck'].map((element) => getCellPercent(row[element])),
      backgroundColor: materialColors[material],
      borderColor: '#ffffff',
      borderWidth: 1,
    };
  });
  materialChart.update();
}

function updateTables() {
  const displayed = getDisplayedFeatures();
  const materialRows = getMaterialRows(displayed);
  renderTable('material-table', buildingElementLabels, materialRows);
  updateMaterialChart(materialRows);

  renderTable('combustibility-table', combustibilityConfig.columns, getCombustibilityRows(displayed));
  for (const config of structureConfigs) {
    renderTable(config.key, config.columns, getStructureRows(displayed, config));
  }
}

function updateDashboard() {
  document.getElementById('map-title').textContent = `${currentFire} fire structures map`;
  updateMap();
  updateDamageChart();
  updateSamplingChart();
  updateTables();
  document.querySelectorAll('#fire-buttons button').forEach((button) => {
    button.classList.toggle('active', button.dataset.fire === currentFire);
  });
}

function makeFireButtons() {
  const host = document.getElementById('fire-buttons');
  host.innerHTML = fires
    .map((fire) => `<button type="button" data-fire="${fire}">${fire}</button>`)
    .join('');

  host.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-fire]');
    if (!button) {
      return;
    }
    currentFire = button.dataset.fire;
    updateDashboard();
  });
}

function makeDamageFilters() {
  const host = document.getElementById('damage-filters');
  host.innerHTML = damageList
    .map((damage) => `
      <label class="damage-filter" style="color:${damageColors[damage]}">
        <input type="checkbox" value="${damage}" checked>
        <span>${damage}</span>
      </label>
    `)
    .join('');

  host.addEventListener('change', () => {
    displayedDamages = [...host.querySelectorAll('input:checked')].map((input) => input.value);
    updateDashboard();
  });
}

async function loadData() {
  const [structureResponse, perimeterResponse] = await Promise.all([
    fetch('data/POSTFIRE_CLEAN_DATA.geojson'),
    fetch('data/WFIGS_INTERAGENCY_PERIMETERS_CLEAN_DATA.geojson'),
  ]);
  const [structureData, perimeterData] = await Promise.all([
    structureResponse.json(),
    perimeterResponse.json(),
  ]);

  structureFeatures = structureData.features;
  perimeterFeatures = perimeterData.features;
}

async function main() {
  makeFireButtons();
  makeDamageFilters();
  initMap();
  initCharts();
  await loadData();
  updateDashboard();
}

main().catch((error) => {
  document.body.innerHTML = `<pre>Unable to load dashboard: ${error.message}</pre>`;
});
