(() => {
const { damageColors, damageList, fires } = window.AppConfig;
const { getDisplayedFeatures, getFireFeatures } = window.DataExtract;
const {
  initCharts,
  initMap,
  updateDamageChart,
  updateMaterialDisplays,
  updateMap,
  updateSamplingChart,
} = window.PlotView;

const appState = {
  charts: null,
  currentFire: 'palisades',
  currentDisplay: 'table',
  displayedDamages: [...damageList],
  map: null,
  perimeterFeatures: [],
  structureFeatures: [],
};

function getCurrentFireFeatures() {
  return getFireFeatures(appState.structureFeatures, appState.currentFire);
}

function getCurrentDisplayedFeatures() {
  return getDisplayedFeatures(
    appState.structureFeatures,
    appState.currentFire,
    appState.displayedDamages,
  );
}

function updateDashboard() {
  const allFeatures = getCurrentFireFeatures();
  const displayedFeatures = getCurrentDisplayedFeatures();

  document.getElementById('map-title').textContent = `${appState.currentFire} fire structures map`;
  document.querySelector('.figure').dataset.display = appState.currentDisplay;

  updateMap(appState.map, displayedFeatures, appState.perimeterFeatures, appState.currentFire);
  updateDamageChart(appState.charts.damageChart, allFeatures, appState.displayedDamages);
  updateSamplingChart(appState.charts.samplingChart, appState.currentFire);
  updateMaterialDisplays(displayedFeatures, appState.charts);

  document.querySelectorAll('#fire-buttons button').forEach((button) => {
    button.classList.toggle('active', button.dataset.fire === appState.currentFire);
  });

  document.querySelectorAll('#display-buttons button').forEach((button) => {
    button.classList.toggle('active', button.dataset.display === appState.currentDisplay);
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

    appState.currentFire = button.dataset.fire;
    updateDashboard();
  });
}

function makeDisplayButtons() {
  const host = document.getElementById('display-buttons');

  host.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-display]');
    if (!button) {
      return;
    }

    appState.currentDisplay = button.dataset.display;
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
    appState.displayedDamages = [...host.querySelectorAll('input:checked')].map((input) => input.value);
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

  appState.structureFeatures = structureData.features;
  appState.perimeterFeatures = perimeterData.features;
}

async function main() {
  makeFireButtons();
  makeDisplayButtons();
  makeDamageFilters();
  appState.map = initMap();
  appState.charts = initCharts();
  await loadData();
  updateDashboard();
}

main().catch((error) => {
  document.body.innerHTML = `<pre>Unable to load dashboard: ${error.message}</pre>`;
});
})();
