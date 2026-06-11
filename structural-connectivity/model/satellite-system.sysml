// Satellite system model used to demonstrate structural connectivity analysis.
// The orphaned 'DebugProbe' block is intentional — the analysis should flag it.

package SatelliteSystem {

    part def Satellite {
        part payload : PayloadAssembly;
        part bus : SpacecraftBus;
        part comms : CommunicationsSubsystem;
    }

    part def PayloadAssembly {
        part imager : OpticalImager;
        part processor : ImageProcessor;
    }

    part def SpacecraftBus {
        part eps : ElectricalPowerSubsystem;
        part adcs : AttitudeControlSubsystem;
        part thermal : ThermalControlSubsystem;
    }

    part def CommunicationsSubsystem {
        part rf : RFTransceiver;
        part antenna : DeployableAntenna;
    }

    part def ElectricalPowerSubsystem {
        part panels : SolarArray;
        part battery : LithiumIonBattery;
        part pdu : PowerDistributionUnit;
    }

    part def AttitudeControlSubsystem {
        part rw1 : ReactionWheel;
        part rw2 : ReactionWheel;
        part rw3 : ReactionWheel;
        part starTracker : StarTracker;
    }

    part def ThermalControlSubsystem {
        part heatPipe : HeatPipe;
        part radiator : Radiator;
    }

    part def OpticalImager {}
    part def ImageProcessor {}
    part def RFTransceiver {}
    part def DeployableAntenna {}
    part def SolarArray {}
    part def LithiumIonBattery {}
    part def PowerDistributionUnit {}
    part def ReactionWheel {}
    part def StarTracker {}
    part def HeatPipe {}
    part def Radiator {}

    // Intentionally orphaned — not used anywhere in the Satellite hierarchy.
    // The structural connectivity analysis should report this as a warning.
    part def DebugProbe {
        part interface : GroundSupportInterface;
    }
    part def GroundSupportInterface {}
}
