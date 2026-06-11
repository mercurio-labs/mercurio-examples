package DecisionReview {
    import ScalarValues::*;

    part def MissionComputer {
        attribute criticality : Real = 4.0;
        attribute latency_ms : Real = 35.0;
    }

    part def ThermalCamera {
        attribute power_w : Real = 18.0;
        attribute mass_kg : Real = 1.7;
    }

    part def Radar {
        attribute power_w : Real = 42.0;
        attribute mass_kg : Real = 4.8;
    }

    part def AirframePayload {
        part computer : MissionComputer;
        part camera : ThermalCamera;
        part radar : Radar;
    }

    requirement def PayloadDecisionObjective {
        doc /* Select a payload architecture that balances mass, power, and sensing coverage. */
    }

    analysis def PayloadArchitectureReview {
        subject payload : AirframePayload;

        objective selectedArchitecture : PayloadDecisionObjective {
            subject = payload;
        }
    }

    action def SelectPayloadMode {
        attribute availablePower_w : Real = 60.0;

        decide evaluatePayload;
        if availablePower_w >= 80.0 then highCoverage;
        if availablePower_w >= 45.0 then balancedCoverage;
        else lowPower;

        action highCoverage;
        action balancedCoverage;
        action lowPower;
    }

    individual part candidatePayload : AirframePayload;

    part reviewContext {
        analysis payloadReview : PayloadArchitectureReview {
            subject payload = candidatePayload;
        }

        action selectPayloadMode : SelectPayloadMode;
    }
}
