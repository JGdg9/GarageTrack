import {
  createMaintenanceRecord,
  createVehicle,
  deleteMaintenanceRecord,
  deleteVehicle,
  getDemoConfiguration,
  getMaintenanceHistory,
  getStatistics,
  getVehicle,
  getVehicleExpenses,
  getVehicles,
  updateMaintenanceRecord,
  updateVehicle,
} from './api.js';
import { createMaintenancePayload, createVehiclePayload } from './form_data.js';

const appRoot = document.querySelector('#app');
const appDialog = document.querySelector('#app-dialog');
const toastRegion = document.querySelector('#toast');
const currencyFormatter = new Intl.NumberFormat('en-IE', {
  style: 'currency',
  currency: 'EUR',
});
const integerFormatter = new Intl.NumberFormat('en-US');
const mutationActions = new Set([
  'new-vehicle',
  'new-maintenance',
  'edit-vehicle',
  'delete-vehicle',
  'edit-maintenance',
  'delete-maintenance',
]);
const state = {
  view: 'dashboard',
  demoReadOnly: true,
  configurationLoaded: false,
  vehicleId: null,
  vehicles: [],
  statistics: null,
  vehicle: null,
  vehicleExpenses: null,
  maintenanceRecords: [],
  isLoading: false,
  error: null,
};
let toastTimeout;

function createElement(tagName, className = '', textContent = '') {
  const element = document.createElement(tagName);
  if (className) {
    element.className = className;
  }
  if (textContent) {
    element.textContent = textContent;
  }
  return element;
}

function createButton(label, action, className = 'button button-secondary') {
  const button = createElement('button', className, label);
  button.type = 'button';
  button.dataset.action = action;
  return button;
}

function createPageHeader() {
  const header = createElement('header', 'page-heading');
  const text = createElement('div', 'page-heading-copy');
  const eyebrow = createElement(
    'p',
    'eyebrow',
    state.demoReadOnly ? 'Public read-only demo' : 'Garage overview',
  );
  const title = createElement('h1', 'page-title');
  const subtitle = createElement('p', 'page-subtitle');
  const actions = createElement('div', 'page-heading-actions');

  if (state.view === 'dashboard') {
    title.textContent = 'Overview';
    subtitle.textContent = state.demoReadOnly
      ? 'Explore the sample vehicles and maintenance history. Editing is disabled.'
      : 'A clear view of your vehicles and their upkeep.';
    if (!state.demoReadOnly) {
      actions.append(createButton('Add vehicle', 'new-vehicle', 'button button-primary'));
    }
  } else if (state.view === 'vehicles') {
    title.textContent = 'Your vehicles';
    subtitle.textContent = state.demoReadOnly
      ? 'Browse the sample vehicle records. Editing is disabled.'
      : 'Keep the details of every vehicle up to date.';
    if (!state.demoReadOnly) {
      actions.append(createButton('Add vehicle', 'new-vehicle', 'button button-primary'));
    }
  } else {
    const hasLoadedVehicle = state.vehicle?.id === state.vehicleId;
    title.textContent = hasLoadedVehicle
      ? `${state.vehicle.brand} ${state.vehicle.model}`
      : 'Vehicle details';
    subtitle.textContent = state.demoReadOnly
      ? 'Maintenance history and lifetime expenses. Editing is disabled.'
      : 'Maintenance history and lifetime expenses.';
    actions.append(createButton('Back to vehicles', 'navigate-vehicles'));
    if (!state.demoReadOnly) {
      actions.append(createButton('Add maintenance', 'new-maintenance', 'button button-primary'));
    }
  }

  text.append(eyebrow, title, subtitle);
  header.append(text, actions);
  return header;
}

function createMetricCard(label, value, note) {
  const card = createElement('article', 'metric-card');
  card.append(
    createElement('p', 'metric-label', label),
    createElement('p', 'metric-value', value),
    createElement('p', 'metric-note', note),
  );
  return card;
}

function createSectionHeading(title, actionLabel, actionName) {
  const heading = createElement('div', 'section-heading');
  heading.append(createElement('h2', 'section-title', title));
  if (actionLabel && actionName) {
    heading.append(createButton(actionLabel, actionName, 'text-button'));
  }
  return heading;
}

function createEmptyState(title, description, actionLabel, actionName) {
  const emptyState = createElement('div', 'empty-state');
  emptyState.append(
    createElement('span', 'empty-state-mark', 'GT'),
    createElement('h3', 'empty-state-title', title),
    createElement('p', 'empty-state-description', description),
  );
  if (actionLabel && actionName) {
    emptyState.append(createButton(actionLabel, actionName, 'button button-primary'));
  }
  return emptyState;
}

function createVehicleLabel(vehicle) {
  return `${vehicle.brand} ${vehicle.model}`;
}

function createDashboardVehicleRow(vehicle) {
  const row = createElement('article', 'vehicle-list-row');
  const details = createElement('div', 'vehicle-list-details');
  const title = createElement('h3', 'vehicle-list-title', createVehicleLabel(vehicle));
  const meta = createElement(
    'p',
    'vehicle-list-meta',
    `${vehicle.year} · ${integerFormatter.format(vehicle.current_mileage)} km`,
  );
  const plate = createElement('span', 'license-plate', vehicle.license_plate || 'No plate');
  const openButton = createButton('View details', 'open-vehicle', 'text-button');
  openButton.dataset.id = vehicle.id;
  details.append(title, meta);
  row.append(details, plate, openButton);
  return row;
}

function renderDashboard() {
  const content = createElement('div', 'content-stack');
  const statistics = state.statistics;
  const metricGrid = createElement('section', 'metric-grid');
  metricGrid.setAttribute('aria-label', 'Garage statistics');
  metricGrid.append(
    createMetricCard(
      'Vehicles',
      integerFormatter.format(statistics.total_vehicles),
      'In your garage',
    ),
    createMetricCard(
      'Maintenance records',
      integerFormatter.format(statistics.total_maintenance_records),
      'Across all vehicles',
    ),
    createMetricCard(
      'Total expenses',
      currencyFormatter.format(Number(statistics.total_expenses)),
      'Lifetime maintenance cost',
    ),
  );

  const vehicleSection = createElement('section', 'surface-card vehicle-overview');
  vehicleSection.append(createSectionHeading('Your vehicles', 'View all', 'navigate-vehicles'));
  if (state.vehicles.length === 0) {
    vehicleSection.append(
      createEmptyState(
        'Your garage is ready',
        state.demoReadOnly
          ? 'This public demo uses sample vehicle records.'
          : 'Add your first vehicle to start keeping track of maintenance and costs.',
        state.demoReadOnly ? null : 'Add a vehicle',
        state.demoReadOnly ? null : 'new-vehicle',
      ),
    );
  } else {
    const vehicleList = createElement('div', 'vehicle-list');
    state.vehicles.slice(0, 5).forEach((vehicle) => {
      vehicleList.append(createDashboardVehicleRow(vehicle));
    });
    vehicleSection.append(vehicleList);
  }

  content.append(metricGrid, vehicleSection);
  return content;
}

function createVehicleCard(vehicle) {
  const card = createElement('article', 'vehicle-card');
  const cardTop = createElement('div', 'vehicle-card-top');
  const plate = createElement('span', 'license-plate', vehicle.license_plate || 'No plate');
  const year = createElement('span', 'vehicle-year', String(vehicle.year));
  const title = createElement('h2', 'vehicle-card-title', createVehicleLabel(vehicle));
  const mileage = createElement(
    'p',
    'vehicle-card-mileage',
    `${integerFormatter.format(vehicle.current_mileage)} km recorded`,
  );
  const actions = createElement('div', 'vehicle-card-actions');
  const detailsButton = createButton('Details', 'open-vehicle', 'button button-primary');
  detailsButton.dataset.id = vehicle.id;
  cardTop.append(plate, year);
  actions.append(detailsButton);
  if (!state.demoReadOnly) {
    const editButton = createButton('Edit', 'edit-vehicle', 'button button-secondary');
    const deleteButton = createButton('Delete', 'delete-vehicle', 'button button-danger');
    editButton.dataset.id = vehicle.id;
    deleteButton.dataset.id = vehicle.id;
    actions.append(editButton, deleteButton);
  }
  card.append(cardTop, title, mileage, actions);
  return card;
}

function renderVehicles() {
  const content = createElement('div', 'content-stack');
  const section = createElement('section', 'surface-card');
  section.append(createSectionHeading('Vehicle collection'));

  if (state.vehicles.length === 0) {
    section.append(
      createEmptyState(
        'No vehicles yet',
        state.demoReadOnly
          ? 'This public demo uses sample vehicle records.'
          : 'Add a vehicle to create its maintenance history and expense summary.',
        state.demoReadOnly ? null : 'Add a vehicle',
        state.demoReadOnly ? null : 'new-vehicle',
      ),
    );
  } else {
    const vehicleGrid = createElement('div', 'vehicle-grid');
    state.vehicles.forEach((vehicle) => vehicleGrid.append(createVehicleCard(vehicle)));
    section.append(vehicleGrid);
  }

  content.append(section);
  return content;
}

function createDefinitionItem(label, value) {
  const item = createElement('div', 'vehicle-definition');
  item.append(
    createElement('dt', 'vehicle-definition-label', label),
    createElement('dd', 'vehicle-definition-value', value),
  );
  return item;
}

function createMaintenanceCard(record) {
  const card = createElement('article', 'maintenance-card');
  const header = createElement('div', 'maintenance-card-header');
  const titleGroup = createElement('div', 'maintenance-card-title-group');
  const title = createElement('h3', 'maintenance-card-title', record.maintenance_type);
  const date = createElement('time', 'maintenance-card-date', formatDate(record.maintenance_date));
  const details = createElement('dl', 'maintenance-card-details');

  date.dateTime = record.maintenance_date;
  titleGroup.append(title, date);
  header.append(
    titleGroup,
    createElement('span', 'cost-pill', currencyFormatter.format(Number(record.cost))),
  );
  details.append(
    createDefinitionItem('Mileage', `${integerFormatter.format(record.mileage)} km`),
    createDefinitionItem('Description', record.description || 'No notes'),
  );
  card.append(header, details);
  if (!state.demoReadOnly) {
    const actions = createElement('div', 'maintenance-card-actions');
    const editButton = createButton('Edit', 'edit-maintenance', 'button button-secondary');
    const deleteButton = createButton('Delete', 'delete-maintenance', 'button button-danger');
    editButton.dataset.id = record.id;
    deleteButton.dataset.id = record.id;
    actions.append(editButton, deleteButton);
    card.append(actions);
  }
  return card;
}

function renderVehicleDetails() {
  const vehicle = state.vehicle;
  const content = createElement('div', 'content-stack');
  const vehicleCard = createElement('section', 'surface-card vehicle-summary-card');
  const summaryHeading = createElement('div', 'section-heading');
  const summaryTitle = createElement('div', 'section-heading-copy');
  const summaryActions = createElement('div', 'section-actions');
  const definitions = createElement('dl', 'vehicle-definitions');

  summaryTitle.append(
    createElement('p', 'eyebrow', 'Vehicle profile'),
    createElement('h2', 'section-title', createVehicleLabel(vehicle)),
  );
  if (!state.demoReadOnly) {
    const editButton = createButton('Edit vehicle', 'edit-vehicle', 'button button-secondary');
    const deleteButton = createButton('Delete vehicle', 'delete-vehicle', 'button button-danger');
    editButton.dataset.id = vehicle.id;
    deleteButton.dataset.id = vehicle.id;
    summaryActions.append(editButton, deleteButton);
  }
  summaryHeading.append(summaryTitle, summaryActions);
  definitions.append(
    createDefinitionItem('Year', String(vehicle.year)),
    createDefinitionItem('License plate', vehicle.license_plate || 'Not provided'),
    createDefinitionItem(
      'Current mileage',
      `${integerFormatter.format(vehicle.current_mileage)} km`,
    ),
    createDefinitionItem(
      'Total expenses',
      currencyFormatter.format(Number(state.vehicleExpenses.total_expenses)),
    ),
  );
  vehicleCard.append(summaryHeading, definitions);

  const maintenanceSection = createElement('section', 'surface-card');
  maintenanceSection.append(
    createSectionHeading(
      'Maintenance history',
      state.demoReadOnly ? null : 'Add maintenance',
      state.demoReadOnly ? null : 'new-maintenance',
    ),
  );
  if (state.maintenanceRecords.length === 0) {
    maintenanceSection.append(
      createEmptyState(
        'No maintenance recorded',
        state.demoReadOnly
          ? 'No sample maintenance records are available for this vehicle.'
          : "Add the first service to start this vehicle's history.",
        state.demoReadOnly ? null : 'Add maintenance',
        state.demoReadOnly ? null : 'new-maintenance',
      ),
    );
  } else {
    const recordList = createElement('div', 'maintenance-list');
    state.maintenanceRecords.forEach((record) => {
      recordList.append(createMaintenanceCard(record));
    });
    maintenanceSection.append(recordList);
  }

  content.append(vehicleCard, maintenanceSection);
  return content;
}

function renderLoadingState() {
  const loading = createElement('div', 'loading-state');
  loading.setAttribute('role', 'status');
  loading.append(
    createElement('span', 'loading-indicator'),
    createElement('p', 'loading-label', 'Loading your garage...'),
  );
  return loading;
}

function renderErrorState() {
  const error = createElement('section', 'surface-card error-state');
  error.setAttribute('role', 'alert');
  error.append(
    createElement('h2', 'section-title', 'GarageTrack could not load this view'),
    createElement('p', 'empty-state-description', state.error),
    createButton('Try again', 'retry', 'button button-primary'),
  );
  return error;
}

function renderPage() {
  if (!appRoot) {
    return;
  }

  const mainContent = state.isLoading
    ? renderLoadingState()
    : state.error
      ? renderErrorState()
      : state.view === 'dashboard'
        ? renderDashboard()
        : state.view === 'vehicles'
          ? renderVehicles()
          : renderVehicleDetails();

  appRoot.setAttribute('aria-busy', String(state.isLoading));
  appRoot.replaceChildren(createPageHeader(), mainContent);

  const activeView = state.view === 'detail' ? 'vehicles' : state.view;
  document.querySelectorAll('[data-view]').forEach((navigationButton) => {
    navigationButton.classList.toggle('is-active', navigationButton.dataset.view === activeView);
  });
}

async function loadCurrentView() {
  state.isLoading = true;
  state.error = null;
  renderPage();

  try {
    if (state.view === 'dashboard') {
      const [statistics, vehicles] = await Promise.all([getStatistics(), getVehicles()]);
      state.statistics = statistics;
      state.vehicles = vehicles;
    } else if (state.view === 'vehicles') {
      state.vehicles = await getVehicles();
    } else {
      const [vehicle, vehicleExpenses, maintenanceRecords] = await Promise.all([
        getVehicle(state.vehicleId),
        getVehicleExpenses(state.vehicleId),
        getMaintenanceHistory(state.vehicleId),
      ]);
      state.vehicle = vehicle;
      state.vehicleExpenses = vehicleExpenses;
      state.maintenanceRecords = maintenanceRecords;
    }
  } catch (error) {
    state.error = getErrorMessage(error);
  } finally {
    state.isLoading = false;
    renderPage();
  }
}

async function initializeApplication() {
  state.isLoading = true;
  state.error = null;
  renderPage();

  try {
    const configuration = await getDemoConfiguration();
    state.demoReadOnly = configuration.demo_read_only;
    state.configurationLoaded = true;
    updateModeIndicator();
    await loadCurrentView();
  } catch (error) {
    state.demoReadOnly = true;
    state.error = getErrorMessage(error);
    state.isLoading = false;
    updateModeIndicator();
    renderPage();
  }
}

function updateModeIndicator() {
  const modeLabel = document.querySelector('#mode-label');
  const modeDescription = document.querySelector('#mode-description');
  if (!modeLabel || !modeDescription) {
    return;
  }

  modeLabel.textContent = state.demoReadOnly ? 'Public demo' : 'Local garage';
  modeDescription.textContent = state.demoReadOnly
    ? 'Read-only sample data'
    : 'Runs on this device';
}

function getErrorMessage(error) {
  return error instanceof Error
    ? error.message
    : 'The request could not be completed. Please try again.';
}

function formatDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`);
  if (Number.isNaN(date.valueOf())) {
    return dateString;
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

function createFormField({
  label,
  name,
  type = 'text',
  value = '',
  required = false,
  min,
  max,
  step,
  wide = false,
}) {
  const field = createElement('div', wide ? 'form-field form-field-wide' : 'form-field');
  const inputId = `field-${name}`;
  const input =
    type === 'textarea'
      ? createElement('textarea', 'form-control')
      : createElement('input', 'form-control');

  input.id = inputId;
  input.name = name;
  if (type !== 'textarea') {
    input.type = type;
  }
  if (value !== undefined && value !== null) {
    input.value = String(value);
  }
  if (required) {
    input.required = true;
  }
  if (min !== undefined) {
    input.min = String(min);
  }
  if (max !== undefined) {
    input.max = String(max);
  }
  if (step !== undefined) {
    input.step = String(step);
  }

  const fieldLabel = createElement('label', 'form-label', label);
  fieldLabel.htmlFor = inputId;
  field.append(fieldLabel, input);
  return field;
}

function createFormActions(submitLabel) {
  const actions = createElement('div', 'dialog-actions');
  actions.append(createButton('Cancel', 'close-dialog', 'button button-secondary'));
  const submitButton = createElement('button', 'button button-primary', submitLabel);
  submitButton.type = 'submit';
  actions.append(submitButton);
  return actions;
}

function createFormFeedback() {
  const feedback = createElement('p', 'form-error');
  feedback.dataset.formError = '';
  feedback.setAttribute('role', 'alert');
  feedback.hidden = true;
  return feedback;
}

function openDialog(title, description, form) {
  const heading = createElement('div', 'dialog-heading');
  heading.append(
    createElement('p', 'eyebrow', 'GarageTrack'),
    createElement('h2', 'dialog-title', title),
    createElement('p', 'dialog-description', description),
  );
  heading.querySelector('h2').id = 'dialog-title';
  appDialog.replaceChildren(heading, form);
  appDialog.showModal();
  form.querySelector('input, textarea')?.focus();
}

function openVehicleDialog(vehicle = null) {
  const currentYear = new Date().getFullYear();
  const form = createElement('form', 'form-stack');
  form.dataset.formType = 'vehicle';
  if (vehicle) {
    form.dataset.recordId = vehicle.id;
  }
  const fields = createElement('div', 'form-grid');
  fields.append(
    createFormField({
      label: 'Brand',
      name: 'brand',
      value: vehicle?.brand ?? '',
      required: true,
    }),
    createFormField({
      label: 'Model',
      name: 'model',
      value: vehicle?.model ?? '',
      required: true,
    }),
    createFormField({
      label: 'Year',
      name: 'year',
      type: 'number',
      value: vehicle?.year ?? currentYear,
      min: 1886,
      max: currentYear + 1,
      step: 1,
      required: true,
    }),
    createFormField({
      label: 'License plate',
      name: 'licensePlate',
      value: vehicle?.license_plate ?? '',
    }),
    createFormField({
      label: 'Current mileage',
      name: 'currentMileage',
      type: 'number',
      value: vehicle?.current_mileage ?? 0,
      min: 0,
      step: 1,
      required: true,
    }),
  );
  form.append(
    fields,
    createFormFeedback(),
    createFormActions(vehicle ? 'Save changes' : 'Add vehicle'),
  );
  openDialog(
    vehicle ? 'Edit vehicle' : 'Add a vehicle',
    'Enter the basic details you use to identify this vehicle.',
    form,
  );
}

function getLocalDate() {
  const today = new Date();
  const localToday = new Date(today.valueOf() - today.getTimezoneOffset() * 60000);
  return localToday.toISOString().slice(0, 10);
}

function openMaintenanceDialog(record = null) {
  const form = createElement('form', 'form-stack');
  form.dataset.formType = 'maintenance';
  if (record) {
    form.dataset.recordId = record.id;
  }
  const fields = createElement('div', 'form-grid');
  fields.append(
    createFormField({
      label: 'Maintenance type',
      name: 'maintenanceType',
      value: record?.maintenance_type ?? '',
      required: true,
    }),
    createFormField({
      label: 'Date',
      name: 'maintenanceDate',
      type: 'date',
      value: record?.maintenance_date ?? getLocalDate(),
      required: true,
    }),
    createFormField({
      label: 'Mileage',
      name: 'mileage',
      type: 'number',
      value: record?.mileage ?? state.vehicle.current_mileage,
      min: 0,
      step: 1,
      required: true,
    }),
    createFormField({
      label: 'Cost (EUR)',
      name: 'cost',
      type: 'number',
      value: record?.cost ?? '0.00',
      min: 0,
      step: '0.01',
      required: true,
    }),
    createFormField({
      label: 'Description',
      name: 'description',
      type: 'textarea',
      value: record?.description ?? '',
      wide: true,
    }),
  );
  form.append(
    fields,
    createFormFeedback(),
    createFormActions(record ? 'Save changes' : 'Add record'),
  );
  openDialog(
    record ? 'Edit maintenance' : 'Add maintenance',
    'Record the service, date, mileage, and cost.',
    form,
  );
}

function showToast(message, type = 'success') {
  window.clearTimeout(toastTimeout);
  toastRegion.textContent = message;
  toastRegion.className = `toast toast--${type}`;
  toastRegion.hidden = false;
  toastTimeout = window.setTimeout(() => {
    toastRegion.hidden = true;
    toastRegion.textContent = '';
  }, 3200);
}

function findVehicle(vehicleId) {
  if (state.vehicle?.id === vehicleId) {
    return state.vehicle;
  }
  return state.vehicles.find((vehicle) => vehicle.id === vehicleId);
}

async function handleAction(actionButton) {
  const action = actionButton.dataset.action;
  const recordId = Number(actionButton.dataset.id);

  if (state.demoReadOnly && mutationActions.has(action)) {
    showToast('This public demo is read-only.', 'error');
    return;
  }

  if (action === 'navigate-vehicles') {
    state.view = 'vehicles';
    state.vehicleId = null;
    await loadCurrentView();
  } else if (action === 'retry') {
    if (state.configurationLoaded) {
      await loadCurrentView();
    } else {
      await initializeApplication();
    }
  } else if (action === 'new-vehicle') {
    openVehicleDialog();
  } else if (action === 'new-maintenance') {
    openMaintenanceDialog();
  } else if (action === 'open-vehicle') {
    state.view = 'detail';
    state.vehicleId = recordId;
    await loadCurrentView();
  } else if (action === 'edit-vehicle') {
    const vehicle = findVehicle(recordId);
    if (vehicle) {
      openVehicleDialog(vehicle);
    }
  } else if (action === 'delete-vehicle') {
    const vehicle = findVehicle(recordId);
    const label = vehicle ? createVehicleLabel(vehicle) : 'this vehicle';
    if (window.confirm(`Delete ${label}? This action cannot be undone.`)) {
      await deleteVehicle(recordId);
      state.view = 'vehicles';
      state.vehicleId = null;
      showToast('Vehicle deleted.');
      await loadCurrentView();
    }
  } else if (action === 'edit-maintenance') {
    const record = state.maintenanceRecords.find((item) => item.id === recordId);
    if (record) {
      openMaintenanceDialog(record);
    }
  } else if (action === 'delete-maintenance') {
    if (window.confirm('Delete this maintenance record? This action cannot be undone.')) {
      await deleteMaintenanceRecord(recordId);
      showToast('Maintenance record deleted.');
      await loadCurrentView();
    }
  } else if (action === 'close-dialog') {
    appDialog.close();
  }
}

async function handleFormSubmit(event) {
  const form = event.target;
  if (!(form instanceof HTMLFormElement) || !form.dataset.formType) {
    return;
  }

  event.preventDefault();
  if (state.demoReadOnly) {
    showToast('This public demo is read-only.', 'error');
    return;
  }
  if (form.dataset.saving === 'true') {
    return;
  }

  form.dataset.saving = 'true';
  form.setAttribute('aria-busy', 'true');
  const submitButton = form.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  const formValues = Object.fromEntries(new FormData(form).entries());

  try {
    if (form.dataset.formType === 'vehicle') {
      const vehicleData = createVehiclePayload(formValues);
      if (form.dataset.recordId) {
        await updateVehicle(Number(form.dataset.recordId), vehicleData);
        showToast('Vehicle updated.');
      } else {
        await createVehicle(vehicleData);
        showToast('Vehicle added.');
      }
    } else {
      const maintenanceData = createMaintenancePayload(formValues);
      if (form.dataset.recordId) {
        await updateMaintenanceRecord(Number(form.dataset.recordId), maintenanceData);
        showToast('Maintenance record updated.');
      } else {
        await createMaintenanceRecord(state.vehicleId, maintenanceData);
        showToast('Maintenance record added.');
      }
    }

    appDialog.close();
    await loadCurrentView();
  } catch (error) {
    const feedback = form.querySelector('[data-form-error]');
    feedback.textContent = getErrorMessage(error);
    feedback.hidden = false;
  } finally {
    if (form.isConnected) {
      form.dataset.saving = 'false';
      form.removeAttribute('aria-busy');
      submitButton.disabled = false;
    }
  }
}

document.body.addEventListener('click', (event) => {
  if (!(event.target instanceof Element)) {
    return;
  }

  const navigationButton = event.target.closest('[data-view]');
  if (navigationButton) {
    event.preventDefault();
    state.view = navigationButton.dataset.view;
    state.vehicleId = null;
    void loadCurrentView();
    return;
  }

  const actionButton = event.target.closest('[data-action]');
  if (actionButton) {
    void handleAction(actionButton).catch((error) => {
      showToast(getErrorMessage(error), 'error');
    });
  }
});

document.addEventListener('submit', (event) => {
  void handleFormSubmit(event);
});

appDialog.addEventListener('click', (event) => {
  if (event.target === appDialog) {
    appDialog.close();
  }
});

void initializeApplication();
