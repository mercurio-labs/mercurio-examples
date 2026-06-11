package SatelliteModel {
  import ISQBase::*;

  import ISQSpaceTime::*;

  import ISQMechanics::*;

  import ISQThermodynamics::*;

  import ISQElectromagnetism::*;

  import SI::*;

  import ScalarValues::*;

  part def Structure {
    attribute dry_mass: ISQBase::MassValue;

    attribute length: ISQBase::LengthValue;

    attribute width: ISQBase::LengthValue;

    attribute height: ISQBase::LengthValue;
  }

  part def PowerSystem {
    attribute mass: ISQBase::MassValue;

    attribute solar_array_area: ISQSpaceTime::AreaValue;

    attribute peak_power: ISQMechanics::PowerValue;

    attribute battery_capacity: ISQThermodynamics::EnergyValue;

    attribute bus_voltage: ISQElectromagnetism::ElectricPotentialValue;
  }

  part def ThermalControl {
    attribute mass: ISQBase::MassValue;

    attribute temp_min: ISQBase::ThermodynamicTemperatureValue;

    attribute temp_max: ISQBase::ThermodynamicTemperatureValue;

    attribute heat_dissipation: ISQMechanics::PowerValue;
  }

  part def Satellite {
    attribute total_mass: ISQBase::MassValue;

    attribute orbit_altitude: ISQBase::LengthValue;

    attribute design_life: ISQBase::DurationValue;

    attribute name: ScalarValues::String;

    part structure: Structure;

    part power: PowerSystem;

    part thermal: ThermalControl;
  }
}
