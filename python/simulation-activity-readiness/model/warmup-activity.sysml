package SimulationActivityReadiness {
    import ScalarValues::*;

    part def Printer {
        attribute temperature : Real = 22.0;

        action warmup {
            action home;
            action heatBed;
        }
    }

    analysis def Warmup :> AnalysisCase {
        subject printer : Printer;
    }
}

