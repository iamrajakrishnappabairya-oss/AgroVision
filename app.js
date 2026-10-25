
const $ = id => document.getElementById(id);

const API_DEFAULT = 'https://agrovision-3jck.onrender.com';

const toast = msg => {
  const t = $('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
};

// Navigation
document.querySelectorAll('[data-target]').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.nav').forEach(nav =>
      nav.classList.toggle('active', nav === button)
    );

    const id = button.dataset.target;
    const element = id === 'overview'
      ? document.querySelector('.hero')
      : $(id);

    element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

document.querySelectorAll('[data-goto]').forEach(button => {
  button.addEventListener('click', () => {
    $(button.dataset.goto)?.scrollIntoView({ behavior: 'smooth' });
  });
});

$('notice-close')?.addEventListener('click', () => {
  document.querySelector('.notice')?.remove();
});

$('settings-open')?.addEventListener('click', () => {
  $('api-url')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  $('api-url')?.focus();
  toast('API URL is configured for AgroVision.');
});

function getApiUrl() {
  const field = $('api-url');
  const entered = field?.value.trim();

  return (entered || API_DEFAULT).replace(/\/+$/, '');
}

function showResult(value, crop, source, inputs, note, isApi) {
  $('result-placeholder').hidden = true;
  $('result-error').hidden = true;
  $('result-content').hidden = false;

  $('yield-value').textContent = Number(value).toFixed(2);
  $('result-crop').textContent = crop;
  $('result-source').textContent = source;
  $('result-inputs').textContent = inputs;
  $('result-note').textContent = note;

  $('result-badge').textContent = isApi ? 'API MODEL' : 'DEMO';
  $('api-status').textContent = isApi
    ? 'Connected to model API'
    : 'Demo estimate · not validated';

  $('model-status').textContent = isApi
    ? 'Model available'
    : 'Demo formula';

  $('model-sub').textContent = isApi
    ? source
    : 'Illustrative estimate only';
}

async function checkApiInfo() {
  const api = getApiUrl();

  $('model-status').textContent = 'Checking model…';
  $('model-sub').textContent = 'Connecting to AgroVision';

  try {
    const healthResponse = await fetch(`${api}/health`);

    if (!healthResponse.ok) {
      throw new Error(`Health check HTTP ${healthResponse.status}`);
    }

    const health = await healthResponse.json();

    const response = await fetch(`${api}/model-info`);

    if (!response.ok) {
      throw new Error(`Model info HTTP ${response.status}`);
    }

    const info = await response.json();

    if (info.model_available === true) {
      $('model-status').textContent = 'Model available';
      $('model-sub').textContent =
        info.model_source || 'Model loaded successfully';
      $('api-status').textContent = 'API connected';
    } else {
      $('model-status').textContent = 'Model unavailable';
      $('model-sub').textContent =
        'Backend is online but the model is unavailable';
      $('api-status').textContent = 'Model unavailable';
    }

    const metricsResponse = await fetch(`${api}/metrics`);

    if (metricsResponse.ok) {
      const metrics = await metricsResponse.json();

      $('metrics-status').textContent =
        metrics.mae != null ? `MAE ${metrics.mae}` : 'Metrics available';

      $('metrics-status').title =
        `RMSE: ${metrics.rmse ?? 'N/A'} | R²: ${metrics.r2 ?? 'N/A'} | ` +
        (metrics.dataset_note || 'Demo data; not real-world validation');
    }

    if (health.status !== 'ok') {
      $('model-sub').textContent += ' · Check API health';
    }
  } catch (error) {
    $('model-status').textContent = 'Connection error';
    $('model-sub').textContent = error.message;
    $('api-status').textContent = 'API connection failed';
  }
}

function demoEstimate(crop, rain, temp, ph, irrigation) {
  const base = {
    Wheat: 2.7,
    Rice: 3.2,
    Maize: 4.1,
    Cotton: 1.6,
    Sugarcane: 65,
    Pulses: 0.9
  }[crop] || 2;

  const rainFactor = Math.max(
    0.35,
    1 - Math.abs(rain - (crop === 'Rice' ? 1200 : 650)) / 1400 * 0.5
  );

  const tempFactor = Math.max(
    0.45,
    1 - Math.abs(temp - (crop === 'Wheat' ? 22 : 28)) / 50
  );

  const phFactor = Math.max(0.65, 1 - Math.abs(ph - 6.5) * 0.08);

  return Math.max(
    0.05,
    base * rainFactor * tempFactor * phFactor * (irrigation ? 1.05 : 0.88)
  );
}

$('prediction-form')?.addEventListener('submit', async event => {
  event.preventDefault();

  const crop = $('crop').value;
  const rainfall = Number($('rainfall').value);
  const temperature = Number($('temperature').value);
  const soil_ph = Number($('soilph').value);
  const irrigation = Number($('irrigation').value);

  if (
    !Number.isFinite(rainfall) ||
    !Number.isFinite(temperature) ||
    !Number.isFinite(soil_ph)
  ) {
    toast('Please enter valid numeric values.');
    return;
  }

  const api = getApiUrl();
  const inputs =
    `${rainfall} mm rain · ${temperature}°C · pH ${soil_ph} · ` +
    `irrigation ${irrigation ? 'yes' : 'no'}`;

  $('result-placeholder').hidden = true;
  $('result-content').hidden = true;
  $('result-error').hidden = true;
  $('api-status').textContent = 'Running prediction…';

  try {
    const response = await fetch(`${api}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop,
        rainfall_mm: rainfall,
        temperature_c: temperature,
        soil_ph,
        irrigation
      })
    });

    if (!response.ok) {
      throw new Error(`Prediction request failed: HTTP ${response.status}`);
    }

    const data = await response.json();
    const prediction = Number(data.predicted_yield_tonnes_per_hectare);

    if (!Number.isFinite(prediction)) {
      throw new Error('API returned an invalid prediction value.');
    }

    showResult(
      prediction,
      crop,
      data.model_source || 'AgroVision API model',
      inputs,
      data.warning ||
        'Estimate only. Real-world agricultural accuracy is not validated.',
      true
    );
  } catch (error) {
    $('result-error').hidden = false;
    $('result-error').textContent =
      `Prediction failed: ${error.message}. Check your internet connection ` +
      'and the API deployment. No simulated result was substituted.';

    $('api-status').textContent = 'API connection failed';
    $('model-status').textContent = 'Prediction unavailable';
    $('model-sub').textContent = 'Check the API connection';
  }
});

$('api-url')?.addEventListener('change', checkApiInfo);

// Check automatically on page load.
document.addEventListener('DOMContentLoaded', checkApiInfo);
checkApiInfo();
