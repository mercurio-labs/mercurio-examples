/**
 * Voron Trident 350 + Indx multi-toolhead — structural model.
 *
 * This file captures the system decomposition and names the analysis case
 * that drives the simulation example. State-machine topology and scenario
 * subjects are authored here and compiled from SysML.
 */
package VoronTrident350 {
    import ScalarValues::*;

    // ── Top-level printer ────────────────────────────────────────────────

    part def VoronPrinter {
        // Build volume
        attribute buildVolume_x : Real = 350.0;   // mm
        attribute buildVolume_y : Real = 350.0;   // mm
        attribute buildVolume_z : Real = 250.0;   // mm

        // Derived sensor readings written by subsystems into the shared
        // context so the printer-level state machine can act on them.
        attribute bed_temperature    : Real = 22.0;   // °C
        attribute hotend_temperature : Real = 22.0;   // °C

        // Sub-systems
        part bed        : HeatedBed;
        part hotend     : Hotend;
        part motion     : CoreXYMotionSystem;
        part toolchanger: IndxToolchanger;
        part electronics: Electronics;

        state lifecycle {
            state Idle;
            state Homing;
            state Heating;
            state Printing;
            state ToolChange;
            state Printing2;

            transition idle_homing first Idle accept start then Homing;
            transition homing_heating first Homing accept after 2.5 then Heating;
            transition heating_printing first Heating accept when bed_temperature >= 105 then Printing;
            transition printing_toolchange first Printing accept after 5.0 then ToolChange;
            transition toolchange_printing2 first ToolChange accept after 3.0 then Printing2;
        }
    }

    // ── Heated bed ───────────────────────────────────────────────────────

    part def HeatedBed {
        attribute temperature   : Real = 22.0;    // °C
        attribute targetTemp    : Real = 110.0;   // °C
        attribute heatRate      : Real = 2.3;     // °C / s  (measured on a Trident 350)
        attribute bedDimension  : Real = 350.0;   // mm  (square)

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

            transition cold_heating first Cold accept after 0.5 then Heating;
            transition heating_ready first Heating accept when temperature >= targetTemp then Ready;
        }
    }

    // ── Hotend / toolhead ────────────────────────────────────────────────

    part def Hotend {
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

            transition cold_heating first Cold accept after 0.5 then Heating;
            transition heating_ready first Heating accept when temperature >= targetTemp then Ready;
        }

        attribute temperature   : Real = 22.0;    // °C
        attribute targetTemp    : Real = 250.0;   // °C
        attribute heatRate      : Real = 5.0;     // °C / s
    }

    // ── CoreXY motion system ─────────────────────────────────────────────

    part def CoreXYMotionSystem {
        attribute position_x : Real = 0.0;   // mm
        attribute position_y : Real = 0.0;   // mm

        part xCarriage : XYCarriage;
        part zDrive[3] : ZLeadscrew;          // Trident = triple-Z
    }

    part def XYCarriage  {}
    part def ZLeadscrew  {}

    // ── Indx multi-toolchanger ───────────────────────────────────────────

    part def IndxToolchanger {
        attribute activeTool : Real = 0.0;    // 0 = T0, 1 = T1, 2 = T2 …

        part dock[6] : ToolDock;
    }

    part def ToolDock {
        attribute occupied : Boolean = true;
    }

    // ── Electronics ──────────────────────────────────────────────────────

    part def Electronics {
        attribute inputVoltage  : Real = 24.0;  // V
        attribute cpuLoad       : Real = 0.0;   // 0..1
    }

    // ── The specific printer individual ──────────────────────────────────

    individual part voron : VoronPrinter;

    analysis def PrintSequence :> AnalysisCase {
        subject printer : VoronPrinter;
        subject bed : HeatedBed;
        subject hotend : Hotend;

        assume constraint = printer.bed_temperature == 22.0;
        assume constraint = printer.hotend_temperature == 22.0;
        assume constraint = bed.temperature == 22.0;
        assume constraint = hotend.temperature == 22.0;

        objective thermalProfile {
            subject = printer.bed.temperature;
        }

        objective hotendProfile {
            subject = printer.hotend.temperature;
        }

        objective printerReadiness {
            subject = printer.bed_temperature;
        }
    }
}
