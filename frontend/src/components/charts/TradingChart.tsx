import { useEffect, useRef, useCallback } from "react";
import {
  createChart,
  CandlestickSeries,
  LineSeries,
  AreaSeries,
} from "lightweight-charts";
import type { IChartApi, ISeriesApi } from "lightweight-charts";
import type { PriceHistory } from "@/types";

type ChartType = "candlestick" | "line" | "area";
export type Timeframe = "1m" | "5m" | "15m" | "1h" | "4h" | "1D" | "1W";

interface TradingChartProps {
  data: PriceHistory[];
  chartType: ChartType;
  isDark?: boolean;
  height?: number;
}

function toChartTime(ts: string): number {
  return Math.floor(new Date(ts).getTime() / 1000) as any;
}

export function TradingChart({
  data,
  chartType,
  isDark = true,
  height = 350,
}: TradingChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | ISeriesApi<"Line"> | ISeriesApi<"Area"> | null>(null);

  const candleData = data.map((d) => ({
    time: toChartTime(d.timestamp) as any,
    open: Number(d.open),
    high: Number(d.high),
    low: Number(d.low),
    close: Number(d.close),
  }));

  const lineData = data.map((d) => ({
    time: toChartTime(d.timestamp) as any,
    value: Number(d.close),
  }));

  const initChart = useCallback(() => {
    if (!containerRef.current || data.length === 0) return;
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
      seriesRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: "transparent" },
        textColor: isDark ? "#9ca3af" : "#6b7280",
      },
      grid: {
        vertLines: { color: isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)" },
        horzLines: { color: isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)" },
      },
      rightPriceScale: {
        borderColor: isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)",
        scaleMargins: { top: 0.1, bottom: chartType === "candlestick" ? 0.2 : 0.1 },
      },
      timeScale: {
        borderColor: isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    if (chartType === "candlestick") {
      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor: "#22c55e",
        downColor: "#ef4444",
        borderUpColor: "#22c55e",
        borderDownColor: "#ef4444",
      });
      candleSeries.setData(candleData);
      seriesRef.current = candleSeries as ISeriesApi<"Candlestick">;
    } else if (chartType === "area") {
      const areaSeries = chart.addSeries(AreaSeries, {
        topColor: "rgba(34, 197, 94, 0.4)",
        bottomColor: "rgba(34, 197, 94, 0)",
        lineColor: "#22c55e",
        lineWidth: 2,
      });
      areaSeries.setData(lineData);
      seriesRef.current = areaSeries as ISeriesApi<"Area">;
    } else {
      const lineSeries = chart.addSeries(LineSeries, {
        color: "#22c55e",
        lineWidth: 2,
      });
      lineSeries.setData(lineData);
      seriesRef.current = lineSeries as ISeriesApi<"Line">;
    }

    chart.timeScale().fitContent();
  }, [data.length, chartType, isDark]);

  useEffect(() => {
    initChart();
    return () => {
      if (chartRef.current && containerRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [initChart]);

  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || data.length === 0) return;
    if (chartType === "candlestick") {
      (seriesRef.current as ISeriesApi<"Candlestick">).setData(candleData);
    } else {
      (seriesRef.current as ISeriesApi<"Line">).setData(lineData);
    }
    chartRef.current.timeScale().fitContent();
  }, [data, chartType, candleData, lineData]);

  return <div ref={containerRef} style={{ height: `${height}px`, width: "100%" }} />;
}
