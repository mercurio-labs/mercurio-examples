package SimulationConstraintsChannels {
    import ScalarValues::*;

    part def ThermalChamber {
        attribute temperature : Real = 20.0;
        attribute targetTemperature : Real = 80.0;
        attribute heatRate : Real = 10.0;

        state lifecycle {
            state Cold;
            state Heating {
                do action integrate {
                    assert constraint {
                        temperature == temperature + heatRate * duration;
                    }
                }
            }
            state Ready;

            transition cold_heating first Cold accept start then Heating;
            transition heating_ready first Heating accept when temperature >= targetTemperature then Ready;
        }
    }

    analysis def HeatProfile :> AnalysisCase {
        subject chamber : ThermalChamber;
        assume constraint = chamber.temperature == 20.0;

        objective chamberTemperature {
            subject = chamber.temperature;
        }
    }
}
