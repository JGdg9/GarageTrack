const API_BASE_URL = '/api/v1';

async function sendRequest(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      method: options.method ?? 'GET',
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error('Unable to connect to GarageTrack. Check that the server is running.');
  }

  if (response.status === 204) {
    return null;
  }

  const responseData = await response.json().catch(() => null);
  if (!response.ok) {
    const errorMessage =
      typeof responseData?.detail === 'string'
        ? responseData.detail
        : 'The request could not be completed. Please try again.';
    throw new Error(errorMessage);
  }

  return responseData;
}

function sendJsonRequest(endpoint, method, data) {
  return sendRequest(endpoint, {
    method,
    body: JSON.stringify(data),
  });
}

export function getVehicles() {
  return sendRequest('/vehicles');
}

export function getDemoConfiguration() {
  return sendRequest('/config');
}

export function getVehicle(vehicleId) {
  return sendRequest(`/vehicles/${vehicleId}`);
}

export function createVehicle(vehicleData) {
  return sendJsonRequest('/vehicles', 'POST', vehicleData);
}

export function updateVehicle(vehicleId, vehicleData) {
  return sendJsonRequest(`/vehicles/${vehicleId}`, 'PUT', vehicleData);
}

export function deleteVehicle(vehicleId) {
  return sendRequest(`/vehicles/${vehicleId}`, { method: 'DELETE' });
}

export function getMaintenanceHistory(vehicleId) {
  return sendRequest(`/vehicles/${vehicleId}/maintenance`);
}

export function createMaintenanceRecord(vehicleId, maintenanceData) {
  return sendJsonRequest(`/vehicles/${vehicleId}/maintenance`, 'POST', maintenanceData);
}

export function updateMaintenanceRecord(maintenanceId, maintenanceData) {
  return sendJsonRequest(`/maintenance/${maintenanceId}`, 'PUT', maintenanceData);
}

export function deleteMaintenanceRecord(maintenanceId) {
  return sendRequest(`/maintenance/${maintenanceId}`, { method: 'DELETE' });
}

export function getVehicleExpenses(vehicleId) {
  return sendRequest(`/vehicles/${vehicleId}/expenses`);
}

export function getStatistics() {
  return sendRequest('/statistics');
}
