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

const samplingAxisLabelPlugin = {
  id: 'samplingAxisLabelPlugin',
  afterDraw(chart) {
    if (chart.canvas.id !== 'sampling-chart') {
      return;
    }

    const { ctx, chartArea, scales } = chart;
    ctx.save();
    ctx.fillStyle = '#151515';
    ctx.font = '8px Arial, Helvetica, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    for (const [index, label] of [...plotSamplingTypes].reverse().entries()) {
      ctx.fillText(label, chartArea.left - 7, scales.y.getPixelForValue(index));
    }

    ctx.restore();
  },
};

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
            font: { size: 8 },
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
            font: { size: 8 },
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

  const materialChart = new Chart(document.getElementById('material-chart'), {
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

  return {
    damageChart,
    materialChart,
    samplingChart,
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

function updateMaterialChart(materialChart, materialRows) {
  materialChart.data.datasets = plotMaterials.map((material) => {
    const row = materialRows.find((candidate) => candidate.material === material);
    return {
      label: material,
      data: ['roof', 'side', 'ground deck', 'elevated deck'].map((element) => plotGetCellPercent(row[element])),
      backgroundColor: plotMaterialColors[material],
      borderColor: '#ffffff',
      borderWidth: 1,
    };
  });
  materialChart.update();
}

function updateTables(displayedFeatures, materialChart) {
  const materialRows = plotGetMaterialRows(displayedFeatures);
  renderTable('material-table', plotBuildingElementLabels, materialRows);
  updateMaterialChart(materialChart, materialRows);

  renderTable('combustibility-table', plotCombustibilityConfig.columns, plotGetCombustibilityRows(displayedFeatures));
  for (const config of plotStructureConfigs) {
    renderTable(config.key, config.columns, plotGetStructureRows(displayedFeatures, config));
  }
}

window.PlotView = {
  initCharts,
  initMap,
  updateDamageChart,
  updateMap,
  updateSamplingChart,
  updateTables,
};
})();
