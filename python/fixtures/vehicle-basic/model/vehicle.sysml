package VehicleExample {
    import ScalarValues::*;

    part def Engine {
        attribute power_kw : Real = 150.0;
    }

    part def Wheel {
        attribute diameter_mm : Real = 600.0;
    }

    part def Vehicle {
        attribute mass_kg : Real = 1200.0;

        part engine : Engine;
        part frontLeft : Wheel;
        part frontRight : Wheel;
        part rearLeft : Wheel;
        part rearRight : Wheel;
    }

    part baselineVehicle : Vehicle;
}
