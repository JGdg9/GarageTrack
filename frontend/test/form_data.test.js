import assert from 'node:assert/strict';
import test from 'node:test';

import { createMaintenancePayload, createVehiclePayload } from '../js/form_data.js';

test('createVehiclePayload trims text and converts numeric fields', () => {
  const vehiclePayload = createVehiclePayload({
    brand: ' Honda ',
    model: ' Civic ',
    year: '2022',
    licensePlate: ' GA 1234 ',
    currentMileage: '15000',
  });

  assert.deepEqual(vehiclePayload, {
    brand: 'Honda',
    model: 'Civic',
    year: 2022,
    license_plate: 'GA 1234',
    current_mileage: 15000,
  });
});

test('createVehiclePayload converts a blank optional plate to null', () => {
  const vehiclePayload = createVehiclePayload({
    brand: 'Toyota',
    model: 'Corolla',
    year: '2021',
    licensePlate: '  ',
    currentMileage: '30000',
  });

  assert.equal(vehiclePayload.license_plate, null);
});

test('createMaintenancePayload keeps cost exact and trims optional description', () => {
  const maintenancePayload = createMaintenancePayload({
    maintenanceType: ' Oil change ',
    maintenanceDate: '2026-01-15',
    mileage: '15000',
    cost: '89.90',
    description: '  Synthetic oil  ',
  });

  assert.deepEqual(maintenancePayload, {
    maintenance_type: 'Oil change',
    maintenance_date: '2026-01-15',
    mileage: 15000,
    cost: '89.90',
    description: 'Synthetic oil',
  });
});

test('createMaintenancePayload converts a blank optional description to null', () => {
  const maintenancePayload = createMaintenancePayload({
    maintenanceType: 'Inspection',
    maintenanceDate: '2026-03-20',
    mileage: '16000',
    cost: '0.00',
    description: '  ',
  });

  assert.equal(maintenancePayload.description, null);
  assert.equal(maintenancePayload.cost, '0.00');
});
