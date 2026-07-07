(() => {
const {
  buildingElementLabels,
  buildingElements,
  combustibleMaterials,
  combustibilityConfig,
  damageList,
  materials,
  nonCombustibleMaterials,
} = window.AppConfig;

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
  const remainder = 100 - rounded.reduce((sum, count) => sum + count, 0);
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

function getFireFeatures(structureFeatures, fireName) {
  return structureFeatures.filter((feature) => cleanValue(feature.properties.INCIDENTNAME) === fireName);
}

function getDisplayedFeatures(structureFeatures, fireName, displayedDamages) {
  return getFireFeatures(structureFeatures, fireName)
    .filter((feature) => displayedDamages.includes(cleanValue(feature.properties.DAMAGE)));
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

window.DataExtract = {
  cleanValue,
  formatCountPercentRows,
  getCellPercent,
  getCombustibilityRows,
  getDamageCounts,
  getDisplayedFeatures,
  getFireFeatures,
  getMaterialRows,
  getRoundedPercentages,
  getStructureRows,
};
})();
