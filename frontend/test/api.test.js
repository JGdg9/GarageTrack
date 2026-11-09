import assert from 'node:assert/strict';
import test from 'node:test';

import { createVehicle, deleteVehicle, getDemoConfiguration, getVehicles } from '../js/api.js';

const originalFetch = globalThis.fetch;

test('getVehicles sends a GET request and returns the vehicle list', async () => {
  let requestUrl;
  let requestOptions;
  globalThis.fetch = async (url, options) => {
    requestUrl = url;
    requestOptions = options;
    return new Response(JSON.stringify([{ id: 1, brand: 'Honda' }]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  };

  try {
    const vehicles = await getVehicles();

    assert.equal(requestUrl, '/api/v1/vehicles');
    assert.equal(requestOptions.method, 'GET');
    assert.deepEqual(vehicles, [{ id: 1, brand: 'Honda' }]);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('getDemoConfiguration reads the public demo mode', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/v1/config');
    assert.equal(options.method, 'GET');
    return new Response(JSON.stringify({ demo_read_only: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  };

  try {
    assert.deepEqual(await getDemoConfiguration(), { demo_read_only: true });
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('createVehicle sends the vehicle as JSON', async () => {
  let requestOptions;
  const vehicleData = {
    brand: 'Honda',
    model: 'Civic',
    year: 2022,
    current_mileage: 15000,
  };
  globalThis.fetch = async (_url, options) => {
    requestOptions = options;
    return new Response(JSON.stringify({ id: 1, ...vehicleData }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    });
  };

  try {
    const createdVehicle = await createVehicle(vehicleData);

    assert.equal(requestOptions.method, 'POST');
    assert.equal(requestOptions.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(requestOptions.body), vehicleData);
    assert.equal(createdVehicle.id, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('deleteVehicle accepts a successful no-content response', async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });

  try {
    assert.equal(await deleteVehicle(1), null);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('HTTP errors expose the API validation message', async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: 'License plate is already registered.' }), {
      status: 409,
      headers: { 'Content-Type': 'application/json' },
    });

  try {
    await assert.rejects(getVehicles(), new Error('License plate is already registered.'));
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('network failures return a clear connection message', async () => {
  globalThis.fetch = async () => {
    throw new TypeError('Connection refused');
  };

  try {
    await assert.rejects(
      getVehicles(),
      new Error('Unable to connect to GarageTrack. Check that the server is running.'),
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});
