const form = document.querySelector('#prediction-form');
const brand = document.querySelector('#brand');
const model = document.querySelector('#model');
const result = document.querySelector('#result');
const submit = document.querySelector('#submit');
const formError = document.querySelector('#form-error');
let options = null;

const money = value => new Intl.NumberFormat('en-IN', {style: 'currency', currency: 'INR', maximumFractionDigits: 0}).format(value);
const fill = (select, values) => values.forEach(value => select.add(new Option(value, value)));

async function loadOptions() {
  const response = await fetch('/options');
  if (!response.ok) throw new Error('Opsi belum tersedia');
  options = await response.json();
  fill(brand, options.brands);
  fill(form.elements.seller_type, options.seller_types);
  fill(form.elements.fuel_type, options.fuel_types);
  fill(form.elements.transmission_type, options.transmission_types);
  fill(form.elements.seats, [2, 3, 4, 5, 6, 7, 8, 9]);
}

brand.addEventListener('change', () => {
  model.replaceChildren(new Option(options?.models_by_brand?.[brand.value]?.length ? 'Pilih model' : 'Model tidak tersedia', ''));
  const models = options?.models_by_brand?.[brand.value] || [];
  fill(model, models);
  model.disabled = models.length === 0;
});

function showError(message) {
  formError.textContent = message;
  result.innerHTML = '<p class="eyebrow">HASIL ESTIMASI</p><h2>Periksa kembali isian</h2><p>Form tetap terisi agar dapat diperbaiki.</p>';
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  formError.textContent = '';
  if (!form.reportValidity()) return;
  submit.disabled = true;
  submit.textContent = 'Menghitung...';
  result.innerHTML = '<p class="eyebrow">HASIL ESTIMASI</p><h2>Menghitung...</h2><p>Model sedang memproses spesifikasi.</p>';
  const data = Object.fromEntries(new FormData(form));
  for (const key of ['vehicle_age', 'km_driven', 'engine', 'seats']) data[key] = Number(data[key]);
  for (const key of ['mileage', 'max_power']) data[key] = Number(data[key]);
  try {
    const response = await fetch('/predict', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(response.status === 422 ? 'Periksa kategori atau nilai input.' : response.status === 503 ? 'Layanan model belum siap.' : 'Terjadi kesalahan server.');
    result.innerHTML = `<p class="eyebrow">HASIL ESTIMASI</p><h2 class="price">${money(body.predicted_price)}</h2><p class="range">Rentang: ${money(body.range_low)} – ${money(body.range_high)}</p><p>${body.range_note}</p><p class="model-version">Model: ${body.model_version}</p><p class="disclaimer"><strong>Disclaimer Akademik:</strong> Hasil ini hanya untuk pembelajaran dan bukan penilaian profesional.</p>`;
    result.scrollIntoView({behavior: 'smooth', block: 'nearest'});
  } catch (error) {
    showError(error instanceof TypeError ? 'Tidak dapat terhubung ke server.' : error.message);
  } finally {
    submit.disabled = false;
    submit.textContent = 'Estimasi harga';
  }
});

loadOptions().catch(() => showError('Opsi form belum dapat dimuat. Jalankan server terlebih dahulu.'));
