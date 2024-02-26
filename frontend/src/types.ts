export type SingleHistogramNode = {
  avg_real: number;
  avg_dp: number;
  avg_quantum_dp: number;
};

export type Errors = {
  dp_error: number;
  quantum_dp_error: number;
};

export interface IHistogramData {
  histogramData: SingleHistogramNode[];
  errorPercentages: Errors;
}

export interface IHistogramYearlyResponse {
  data: IHistogramData[];
  labels: string[];
}
