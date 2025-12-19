export class ReactivityLayer {
    reactivity: number = 0.0;
    neutron_flux: number = 0.001;
    period: number = 999.0;
    xenon: number = 0.0;

    update(rods_pos: number, temp: number, dt: number): number {
        // 1. Control Rod Worth (0-100%, 0=Out/+ reactivity)
        // 50% = 0 reactivity. <50% = +reactivity.
        // Range +/- 0.05
        const rho_rods = (50.0 - rods_pos) * 0.002;

        // 2. Thermal Feedback (Doppler)
        // Temp > 300 reduces reactivity
        const temp_delta = temp - 300.0;
        const rho_temp = -0.0001 * temp_delta;

        // 3. Xenon (Simplified)
        if (this.neutron_flux > 1.2) {
            this.xenon += 0.00005 * dt;
        } else {
            this.xenon *= 0.999;
        }

        this.reactivity = rho_rods + rho_temp - this.xenon;

        // Period Calculation
        if (Math.abs(this.reactivity) < 0.00001) {
            this.period = 9999.0;
        } else {
            this.period = 0.08 / this.reactivity;
        }

        // Flux Update
        const growth_factor = this.reactivity * dt * 5.0;
        this.neutron_flux *= (1.0 + growth_factor);
        this.neutron_flux = Math.max(0.0, this.neutron_flux);

        return this.neutron_flux;
    }
}

export class ThermalLayer {
    core_temp: number = 300.0; // Celsius
    status: string = "Stable";

    update(flux: number, pump_speed: number, cooling_eff: number, dt: number): number {
        const power_mw = flux * 2000.0;

        const flow_factor = pump_speed / 100.0;
        const eff_factor = cooling_eff / 100.0;
        const heat_removal = flow_factor * eff_factor * 2500.0;

        const net_heat = power_mw - (heat_removal * (this.core_temp / 600.0));

        // Temp Rise
        this.core_temp += net_heat * 0.05 * dt;

        // Ambient Loss
        this.core_temp -= (this.core_temp - 25.0) * 0.001 * dt;
        this.core_temp = Math.max(25.0, this.core_temp);

        // Status
        if (this.core_temp > 600) this.status = "MELTDOWN";
        else if (this.core_temp > 450) this.status = "CRITICAL";
        else if (this.core_temp > 350) this.status = "Unstable";
        else this.status = "Nominal";

        return this.core_temp;
    }
}

export class SafetyLayer {
    scram_status: boolean = false;
    alerts: string[] = [];
    interlocks_active: boolean = true;

    check(flux: number, temp: number, flow: number, manual_scram: boolean): boolean {
        this.alerts = [];

        if (manual_scram) {
            this.scram_status = true;
            this.alerts.push("MANUAL SCRAM");
        }

        if (this.interlocks_active) {
            if (temp > 420.0) {
                this.scram_status = true;
                this.alerts.push(`TEMP HIGH TRIP (${temp.toFixed(0)}C)`);
            }
            if (flux > 1.15) {
                this.scram_status = true;
                this.alerts.push(`FLUX HIGH TRIP (${(flux * 100).toFixed(0)}%)`);
            }
            if (flow < 10.0 && flux > 0.1) {
                this.scram_status = true;
                this.alerts.push("LOSS OF FLOW TRIP");
            }
        }

        return this.scram_status;
    }
}

export interface Telemetry {
    flux: number;
    power_mw: number;
    temp: number;
    reactivity: number;
    period: number;
    alerts: string[];
    scram: boolean;
}

export interface ControlState {
    rods_pos: number;
    pump_speed: number;
    cooling_eff: number;
    manual_scram: boolean;
    safety_enabled: boolean;
}

export class ReactorUnit {
    id: string;
    name: string;

    physics = new ReactivityLayer();
    thermal = new ThermalLayer();
    safety = new SafetyLayer();

    controls: ControlState = {
        rods_pos: 50.0,
        pump_speed: 100.0,
        cooling_eff: 100.0,
        manual_scram: false,
        safety_enabled: true
    };

    telemetry: Telemetry = {
        flux: 0.001,
        power_mw: 0.0,
        temp: 300.0,
        reactivity: 0.0,
        period: 999.0,
        alerts: [],
        scram: false
    };

    history: any[] = [];
    time: number = 0;

    constructor(id: string, name: string) {
        this.id = id;
        this.name = name;
    }

    tick(dt: number) {
        this.time += dt;
        const c = this.controls;

        // Safety
        this.safety.interlocks_active = c.safety_enabled;
        const is_scrammed = this.safety.check(
            this.telemetry.flux,
            this.telemetry.temp,
            c.pump_speed,
            c.manual_scram
        );

        if (is_scrammed) {
            c.rods_pos = Math.min(100.0, c.rods_pos + 10.0 * dt);
            c.manual_scram = false; // Latch reset handled by logic if needed, simplify here
        }

        // Physics
        const flux = this.physics.update(c.rods_pos, this.telemetry.temp, dt);

        // Thermal
        const temp = this.thermal.update(flux, c.pump_speed, c.cooling_eff, dt);

        // Telemetry
        this.telemetry = {
            flux,
            power_mw: flux * 2000.0,
            temp,
            reactivity: this.physics.reactivity,
            period: this.physics.period,
            alerts: this.safety.alerts,
            scram: is_scrammed
        };

        // History (Every 1s sim time for smoother graphs)
        if (this.time % 1 < dt) {
            this.history.push({
                time: Math.floor(this.time),
                power: this.telemetry.power_mw,
                temp: this.telemetry.temp,
                reactivity: this.telemetry.reactivity * 100000
            });
            if (this.history.length > 100) this.history.shift();
        }
    }
}
