export interface ServiceHealth {
    healthy: number;
    warning: number;
    critical: number;
}
export interface Alert {
    id: number | string;
    severity: string;
    message: string;
    service: string;
    time?: string;
    timestamp?: string;
    status?: string;
}
export interface ErrorBudget {
    total: number;
    consumed: number;
    remaining: number;
}
export interface RequestRate {
    time: string;
    rate: number;
}
export interface OverviewData {
    serviceHealth: ServiceHealth;
    activeAlerts: Alert[];
    errorBudget: ErrorBudget;
    requestRates: RequestRate[];
}
export interface Service {
    id: string | number;
    name: string;
    status: string;
    uptime?: string;
    version?: string;
    owner?: string;
}
export interface SLO {
    id: string | number;
    service: string;
    metric: string;
    target: string | number;
    current: string | number;
    status: string;
}
export interface Experiment {
    id: string | number;
    name?: string;
    type: string;
    status: string;
    target: string;
    result?: string;
    parameters?: Record<string, unknown>;
    start_time?: string;
    end_time?: string;
}
