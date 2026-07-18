const led = document.getElementById('led');
const statusText = document.getElementById('status-text');
const armBtn = document.getElementById('arm-btn');
const lightsBtn = document.getElementById('lights-btn');
const eventLog = document.getElementById('event-log');
const motionEl = document.getElementById('sensor-motion');
const doorEl = document.getElementById('sensor-door');
const climateEl = document.getElementById('sensor-climate');

let armed = false;
let lightsOn = false;

async function fetchStatus() {
  const res = await fetch('/api/status');
  const data = await res.json();
  armed = data.armed;
  lightsOn = data.lights === 'on';

  renderStatus();
  renderEvents(data.events);
}

function renderStatus() {
  led.className = 'led' + (armed ? ' armed' : '');
  statusText.textContent = armed ? 'ARMED' : 'DISARMED';
  armBtn.textContent = armed ? 'DISARM SYSTEM' : 'ARM SYSTEM';
  armBtn.className = 'big-toggle' + (armed ? ' armed' : '');
  lightsBtn.textContent = lightsOn ? '● ON' : '— OFF';
  lightsBtn.className = 'chip' + (lightsOn ? ' on' : '');
}

function renderEvents(events) {
  eventLog.innerHTML = '';
  let latestMotion = null;
  let latestDoor = null;
  let latestClimate = null;

  events.forEach(ev => {
    const row = document.createElement('div');
    row.className = 'row';
    const t = new Date(ev.timestamp * 1000).toLocaleTimeString();
    row.innerHTML = `<span class="time">${t}</span><span class="sev-${ev.severity}">[${ev.source}] ${ev.event_type} — ${ev.detail || ''}</span>`;
    eventLog.appendChild(row);

    if (!latestMotion && ev.source === 'motion_sensor') latestMotion = ev;
    if (!latestDoor && ev.source === 'door_sensor') latestDoor = ev;
    if (!latestClimate && ev.source === 'climate_sensor') latestClimate = ev;
  });

  motionEl.textContent = latestMotion ? 'DETECTED' : 'CLEAR';
  motionEl.className = 'sensor-value' + (latestMotion ? ' alert' : '');

  doorEl.textContent = latestDoor ? 'OPENED' : 'CLOSED';
  doorEl.className = 'sensor-value' + (latestDoor ? ' alert' : '');

  climateEl.textContent = latestClimate ? latestClimate.detail.split(',')[0] : '—';
}

armBtn.addEventListener('click', async () => {
  const endpoint = armed ? '/api/disarm' : '/api/arm';
  await fetch(endpoint, { method: 'POST' });
  fetchStatus();
});

lightsBtn.addEventListener('click', async () => {
  await fetch('/api/lights', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ on: !lightsOn }),
  });
  fetchStatus();
});

fetchStatus();
setInterval(fetchStatus, 2500);
