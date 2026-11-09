export function createVehiclePayload(formValues) {
  const licensePlate = formValues.licensePlate.trim();

  return {
    brand: formValues.brand.trim(),
    model: formValues.model.trim(),
    year: Number(formValues.year),
    license_plate: licensePlate || null,
    current_mileage: Number(formValues.currentMileage),
  };
}

export function createMaintenancePayload(formValues) {
  const description = formValues.description.trim();

  return {
    maintenance_type: formValues.maintenanceType.trim(),
    maintenance_date: formValues.maintenanceDate,
    mileage: Number(formValues.mileage),
    cost: formValues.cost.trim(),
    description: description || null,
  };
}
