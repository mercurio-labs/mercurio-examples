package SensorSystem {
  import ISQBase::'*';

  import ISQSpaceTime::'*';

  import ISQElectromagnetism::'*';

  import ScalarValues::'*';

  part def TemperatureSensor {
    attribute mass: ISQBase::MassValue;

    attribute sampling_rate: ISQSpaceTime::FrequencyValue;

    attribute supply_voltage: ISQElectromagnetism::ElectricPotentialValue;
  }

  part def PressureSensor {
    attribute mass: ISQBase::MassValue;

    attribute sampling_rate: ISQSpaceTime::FrequencyValue;

    attribute supply_voltage: ISQElectromagnetism::ElectricPotentialValue;
  }

  part def SensorArray {
    attribute total_mass: ISQBase::MassValue;

    attribute channel_count: ScalarValues::Integer;

    part temperature_sensor: TemperatureSensor;

    part pressure_sensor: PressureSensor;

    part humidity_sensor: HumiditySensor;

    attribute power_budget: ISQMechanics::PowerValue;
  }

  part def HumiditySensor {
    attribute mass: ISQBase::MassValue;

    attribute sampling_rate: ISQSpaceTime::FrequencyValue;

    attribute resolution: ScalarValues::Real;
  }
}
