package VehicleMassCompliance {
    import ScalarValues::*;

    part def Chassis {
        attribute mass_kg : Real = 400.0;
    }

    part def Battery {
        attribute mass_kg : Real = 550.0;
        attribute capacity_kwh : Real = 80.0;
    }

    part def Motor {
        attribute mass_kg : Real = 120.0;
        attribute power_kw : Real = 220.0;
    }

    part def Vehicle {
        attribute max_mass_kg : Real = 1500.0;

        part chassis : Chassis;
        part battery : Battery;
        part motor : Motor;
    }

    requirement def VehicleMassRequirement {
        doc /*
         * The configured vehicle mass shall be less than or equal to 1500 kg.
         *
         * Intended formal check:
         * total_mass_kg <= max_mass_kg
         */
    }

    analysis def VehicleMassComplianceAnalysis {
        subject vehicle : Vehicle;

        objective massRequirement : VehicleMassRequirement {
            subject = vehicle;
        }

        doc /*
         * Intended calculation:
         * total_mass_kg = chassis.mass_kg + battery.mass_kg + motor.mass_kg
         *
         * Expected result for the fixture:
         * total_mass_kg = 1070
         * max_mass_kg = 1500
         * margin_kg = 430
         * verdict = pass
         */
    }

    part baselineVehicle : Vehicle;

    part analysisContext {
        analysis massCompliance : VehicleMassComplianceAnalysis {
            subject vehicle = baselineVehicle;
        }
    }
}
