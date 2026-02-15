export interface Currency {
  code: string;
  name: string;
  symbol: string;
}

export interface ExchangeRate {
  id: string;
  base_currency: string;
  target_currency: string;
  rate: string;
  date: string;
  fetched_at: string;
}

export interface LatestRates {
  base: string;
  date: string;
  rates: Record<string, string>;
}

export interface HistoricalRates {
  base: string;
  rates: Record<string, Record<string, string>>;
}
