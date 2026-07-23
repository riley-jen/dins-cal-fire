(() => {
const {
  buildingElementLabels: plotBuildingElementLabels,
  combustibilityConfig: plotCombustibilityConfig,
  damageColors: plotDamageColors,
  damageList: plotDamageList,
  materialColors: plotMaterialColors,
  materials: plotMaterials,
  samplingColors: plotSamplingColors,
  samplingData: plotSamplingData,
  samplingTypes: plotSamplingTypes,
  structureConfigs: plotStructureConfigs,
} = window.AppConfig;

const {
  cleanValue: plotCleanValue,
  getCellPercent: plotGetCellPercent,
  getCombustibilityRows: plotGetCombustibilityRows,
  getDamageCounts: plotGetDamageCounts,
  getMaterialRows: plotGetMaterialRows,
  getRoundedPercentages: plotGetRoundedPercentages,
  getStructureRows: plotGetStructureRows,
} = window.DataExtract;

function renderTable(hostId, columns, rows) {
  const host = document.getElementById(hostId);
  const header = columns.map((column) => `<th>${column}</th>`).join('');
  const body = rows
    .map((row) => `<tr>${columns.map((column) => `<td>${row[column]}</td>`).join('')}</tr>`)
    .join('');

  host.innerHTML = `<table><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table>`;
}

const combustibilityColors = {
  combustible: '#B22222',
  'non-combustible': '#4682B4',
  'n/a': '#D3D3D3',
};

const structureElementColors = {
  enclosed: '#B22222',
  unenclosed: '#4682B4',
  '<= 1/8"': '#4682B4',
  '> 1/8"': '#B22222',
  unscreened: '#FFD700',
  'single pane': '#B22222',
  'multi pane': '#4682B4',
  'n/a': '#D3D3D3',
};

const minYearBuilt = 1895;
const maxYearBuilt = 2025;
const minLabeledYearBuilt = 1900;
const maxLabeledYearBuilt = 2020;

const samplingAxisLabelPlugin = {
  id: 'samplingAxisLabelPlugin',
  afterDraw(chart) {
    if (chart.canvas.id !== 'sampling-chart') {
      return;
    }

    const { ctx, chartArea, scales } = chart;
    ctx.save();
    ctx.fillStyle = '#151515';
    ctx.font = '9px Arial, Helvetica, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    for (const [index, label] of [...plotSamplingTypes].reverse().entries()) {
      ctx.fillText(label, chartArea.left - 7, scales.y.getPixelForValue(index));
    }

    ctx.restore();
  },
};

function makeStackedBarChart(canvasId, labels, compact = false) {
  return new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: {
      labels,
      datasets: [],
    },
    options: {
      indexAxis: 'y',
      animation: false,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: compact ? 2 : 0,
          bottom: compact ? 12 : 0,
        },
      },
      scales: {
        x: {
          stacked: true,
          min: 0,
          max: 100,
          display: false,
        },
        y: {
          stacked: true,
          display: !compact,
          grid: { display: false },
          ticks: {
            autoSkip: false,
            color: '#151515',
            font: { size: compact ? 10 : 12 },
          },
        },
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: compact ? 9 : 12,
            padding: compact ? 12 : 10,
            font: { size: compact ? 10 : 11 },
          },
        },
        tooltip: { enabled: false },
      },
    },
  });
}

function initMap() {
  const map = L.map('map', {
    zoomControl: false,
    renderer: L.canvas(),
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap',
  }).addTo(map);

  return {
    map,
    perimeterLayer: null,
    structureLayer: null,
  };
}

function updateMap(mapState, displayedFeatures, perimeterFeatures, currentFire) {
  if (mapState.structureLayer) {
    mapState.structureLayer.remove();
  }
  if (mapState.perimeterLayer) {
    mapState.perimeterLayer.remove();
  }

  mapState.structureLayer = L.geoJSON(displayedFeatures, {
    pointToLayer(feature, latlng) {
      const damage = plotCleanValue(feature.properties.DAMAGE);
      return L.circleMarker(latlng, {
        radius: 2,
        stroke: false,
        fillColor: plotDamageColors[damage],
        fillOpacity: 0.8,
      });
    },
  }).addTo(mapState.map);

  mapState.perimeterLayer = L.geoJSON(
    perimeterFeatures.filter((feature) => plotCleanValue(feature.properties.poly_IncidentName) === currentFire),
    {
      style: {
        color: 'blue',
        fillColor: 'blue',
        fillOpacity: 0.3,
        opacity: 0.6,
        weight: 1,
      },
    },
  ).addTo(mapState.map);

  const bounds = L.featureGroup([mapState.structureLayer, mapState.perimeterLayer]).getBounds();
  if (bounds.isValid()) {
    mapState.map.fitBounds(bounds.pad(0.08), { animate: false });
  }
}

function initCharts() {
  const damageChart = new Chart(document.getElementById('damage-chart'), {
    type: 'pie',
    data: {
      labels: plotDamageList,
      datasets: [{
        data: plotDamageList.map(() => 0),
        backgroundColor: plotDamageList.map((damage) => plotDamageColors[damage]),
        borderWidth: 0,
      }],
    },
    options: {
      animation: false,
      aspectRatio: 1,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
    },
  });

  const samplingChart = new Chart(document.getElementById('sampling-chart'), {
    type: 'scatter',
    data: { datasets: [] },
    options: {
      animation: false,
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: 84,
          right: 4,
          top: 2,
          bottom: 0,
        },
      },
      scales: {
        x: {
          min: -0.5,
          max: 0.5,
          grid: { color: '#d9d9d9' },
          ticks: {
            color: '#151515',
            font: { size: 10 },
            callback: () => '',
          },
        },
        y: {
          min: -0.5,
          max: plotSamplingTypes.length - 0.5,
          grid: { color: '#d9d9d9' },
          ticks: {
            display: false,
            color: '#151515',
            font: { size: 10 },
            stepSize: 1,
            callback(value) {
              return [...plotSamplingTypes].reverse()[value] || '';
            },
          },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
    plugins: [samplingAxisLabelPlugin],
  });

  const materialChart = makeStackedBarChart(
    'material-chart',
    ['roof', 'side', 'ground deck', 'elevated deck'],
  );
  const combustibilityChart = makeStackedBarChart(
    'combustibility-chart',
    ['roof', 'side', 'ground deck', 'elevated deck', 'patio cover', 'fence'],
  );
  const eavesChart = makeStackedBarChart('eaves-chart', ['eaves'], true);
  const ventscreenChart = makeStackedBarChart('ventscreen-chart', ['mesh screen'], true);
  const windowpaneChart = makeStackedBarChart('windowpane-chart', ['window pane'], true);
  const yearBuiltChart = new Chart(document.getElementById('year-built-chart'), {
    type: 'bar',
    data: {
      labels: getYearRange(),
      datasets: [],
    },
    options: {
      animation: false,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 2,
          right: 4,
          bottom: 0,
          left: 0,
        },
      },
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          ticks: {
            color: '#151515',
            font: { size: 7 },
            maxRotation: 0,
            autoSkip: false,
            callback(value) {
              const year = this.getLabelForValue(value);
              const numericYear = Number(year);
              if (
                numericYear < minLabeledYearBuilt
                || numericYear > maxLabeledYearBuilt
                || (numericYear - minLabeledYearBuilt) % 20 !== 0
              ) {
                return '';
              }
              return year;
            },
          },
          title: {
            display: true,
            text: 'year built',
            color: '#151515',
            font: { size: 8 },
            padding: { top: 0 },
          },
        },
        y: {
          stacked: true,
          beginAtZero: true,
          grid: { color: '#d9d9d9' },
          ticks: {
            color: '#151515',
            font: { size: 7 },
            precision: 0,
          },
          title: {
            display: true,
            text: 'number of buildings',
            color: '#151515',
            font: { size: 8 },
            padding: { bottom: 2 },
          },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title(items) {
              return `year: ${items[0].label}`;
            },
            label(item) {
              return [
                `damage: ${item.dataset.label}`,
                `count: ${item.raw}`,
              ];
            },
          },
          filter(item) {
            return item.raw > 0;
          },
        },
      },
    },
  });

  return {
    combustibilityChart,
    damageChart,
    eavesChart,
    materialChart,
    samplingChart,
    ventscreenChart,
    windowpaneChart,
    yearBuiltChart,
  };
}

function updateDamageChart(damageChart, allFeatures, displayedDamages) {
  const counts = plotGetDamageCounts(allFeatures);
  const visibleCounts = plotDamageList.map((damage) => (displayedDamages.includes(damage) ? counts[damage] : 0));
  const total = visibleCounts.reduce((sum, count) => sum + count, 0);
  const fireTotal = allFeatures.length;

  damageChart.data.datasets[0].data = visibleCounts;
  damageChart.update();

  const percentages = plotGetRoundedPercentages(visibleCounts);
  const rows = plotDamageList
    .map((damage, index) => {
      const count = visibleCounts[index];
      return `
        <div class="legend-row">
          <span class="legend-swatch" style="background:${plotDamageColors[damage]}"></span>
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

function updateSamplingChart(samplingChart, currentFire) {
  const data = plotSamplingData[currentFire] || [];
  const dates = data.map(([date]) => date);
  const datePositions = Object.fromEntries(dates.map((date, index) => [date, index]));
  const typePositions = Object.fromEntries(
    plotSamplingTypes.map((type, index) => [type, plotSamplingTypes.length - index - 1]),
  );

  samplingChart.data.datasets = plotSamplingTypes.map((type) => ({
    label: type,
    data: data
      .filter(([, types]) => types.includes(type))
      .map(([date]) => ({ x: datePositions[date], y: typePositions[type] })),
    pointRadius: 5,
    pointBackgroundColor: plotSamplingColors[type],
    pointBorderColor: '#ffffff',
    pointBorderWidth: 1,
  }));
  samplingChart.options.scales.x.max = Math.max(dates.length - 0.5, 0.5);
  samplingChart.options.scales.x.ticks.callback = (value) => dates[value] || '';
  samplingChart.update();
}

function getYearRange() {
  return Array.from(
    { length: maxYearBuilt - minYearBuilt + 1 },
    (_, index) => minYearBuilt + index,
  );
}

function getYearBuiltCounts(features) {
  const counts = Object.fromEntries(
    getYearRange().map((year) => [
      year,
      Object.fromEntries(plotDamageList.map((damage) => [damage, 0])),
    ]),
  );
  const sideCounts = {
    unspecified: 0,
    outOfRange: 0,
  };

  for (const feature of features) {
    const damage = plotCleanValue(feature.properties.DAMAGE);
    if (!plotDamageList.includes(damage)) {
      continue;
    }

    const year = Number(feature.properties.YEARBUILT);
    if (!Number.isFinite(year) || year <= 0) {
      sideCounts.unspecified += 1;
    } else if (year < minYearBuilt || year > maxYearBuilt) {
      sideCounts.outOfRange += 1;
    } else {
      counts[Math.trunc(year)][damage] += 1;
    }
  }

  return { counts, sideCounts };
}

function updateYearBuiltChart(yearBuiltChart, displayedFeatures) {
  const years = getYearRange();
  const { counts, sideCounts } = getYearBuiltCounts(displayedFeatures);

  yearBuiltChart.data.labels = years;
  yearBuiltChart.data.datasets = plotDamageList.map((damage) => ({
    label: damage,
    data: years.map((year) => counts[year][damage]),
    backgroundColor: plotDamageColors[damage],
    borderColor: '#ffffff',
    borderWidth: 0.2,
    barPercentage: 1,
    categoryPercentage: 1,
  }));
  yearBuiltChart.update();

  document.getElementById('year-built-unspecified').textContent = sideCounts.unspecified;
  document.getElementById('year-built-out-of-range').textContent = sideCounts.outOfRange;
}

function updateStackedBarChart(chart, rows, rowColumn, valueColumns, colors) {
  chart.data.labels = valueColumns;
  chart.data.datasets = rows.map((row) => {
    const rowName = row[rowColumn];
    return {
      label: rowName,
      data: valueColumns.map((column) => plotGetCellPercent(row[column])),
      backgroundColor: colors[rowName],
      borderColor: '#ffffff',
      borderWidth: 1,
    };
  });
  chart.update();
}

function updateMaterialChart(materialChart, materialRows) {
  updateStackedBarChart(
    materialChart,
    materialRows,
    'material',
    ['roof', 'side', 'ground deck', 'elevated deck'],
    plotMaterialColors,
  );
}

function updateCombustibilityChart(combustibilityChart, combustibilityRows) {
  updateStackedBarChart(
    combustibilityChart,
    combustibilityRows,
    'combustibility',
    ['roof', 'side', 'ground deck', 'elevated deck', 'patio cover', 'fence'],
    combustibilityColors,
  );
}

function updateStructureChart(chart, config, rows) {
  updateStackedBarChart(
    chart,
    rows,
    config.columns[0],
    config.columns.slice(1),
    structureElementColors,
  );
}

function updateMaterialDisplays(displayedFeatures, charts) {
  const materialRows = plotGetMaterialRows(displayedFeatures);
  renderTable('material-table', plotBuildingElementLabels, materialRows);
  updateMaterialChart(charts.materialChart, materialRows);

  const combustibilityRows = plotGetCombustibilityRows(displayedFeatures);
  renderTable('combustibility-table', plotCombustibilityConfig.columns, combustibilityRows);
  updateCombustibilityChart(charts.combustibilityChart, combustibilityRows);

  const structureCharts = {
    'eaves-table': charts.eavesChart,
    'ventscreen-table': charts.ventscreenChart,
    'windowpane-table': charts.windowpaneChart,
  };
  for (const config of plotStructureConfigs) {
    const rows = plotGetStructureRows(displayedFeatures, config);
    renderTable(config.key, config.columns, rows);
    updateStructureChart(structureCharts[config.key], config, rows);
  }
}

window.PlotView = {
  initCharts,
  initMap,
  updateDamageChart,
  updateMaterialDisplays,
  updateMap,
  updateSamplingChart,
  updateYearBuiltChart,
};
})();
