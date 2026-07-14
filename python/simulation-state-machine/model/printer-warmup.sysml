package SimulationStateMachine {
    import ScalarValues::*;

    part def Printer {
        attribute bed_temperature : Real = 22.0;
        attribute targetTemp : Real = 110.0;
        attribute heatRate : Real = 2.3;

        state lifecycle {
            state Idle;
            state Printing;

            transition start first Idle accept start then Printing;
        }
    }

    analysis def PrintSequence :> AnalysisCase {
        subject printer : Printer;
        assume constraint = printer.bed_temperature == 22.0;
    }
}

