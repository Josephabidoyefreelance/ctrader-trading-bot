import { useEffect, useRef, useState } from "react";
import Chart from "chart.js/auto";

export default function LiveChart() {
  const chartRef = useRef(null);
  const [chartInstance, setChartInstance] = useState(null);

  useEffect(() => {
    const ctx = chartRef.current.getContext("2d");
    const chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          { label: "Price", data: [], borderColor: "green", tension: 0.3 },
          { label: "EMA100", data: [], borderColor: "orange", tension: 0.3 },
          { label: "EMA300", data: [], borderColor: "red", tension: 0.3 },
          { label: "Supertrend", data: [], borderColor: "blue", borderDash: [5,5], tension: 0.3 },
        ],
      },
      options: { responsive: true, plugins: { legend: { position: "top" } } },
    });
    setChartInstance(chart);

    const socket = new WebSocket("ws://127.0.0.1:8000/ws/chart");
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (!chart) return;

      chart.data.labels.push(data.timestamp);
      chart.data.datasets[0].data.push(data.price);
      chart.data.datasets[1].data.push(data.ema100);
      chart.data.datasets[2].data.push(data.ema300);
      chart.data.datasets[3].data.push(data.supertrend);

      // Add signal as dot
      if (data.signal === "BUY") chart.data.datasets[0].pointBackgroundColor?.push("green");
      else if (data.signal === "SELL") chart.data.datasets[0].pointBackgroundColor?.push("red");
      else chart.data.datasets[0].pointBackgroundColor?.push("transparent");

      // Keep last 50 points
      if (chart.data.labels.length > 50) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(d => d.data.shift());
        chart.data.datasets.forEach(d => d.pointBackgroundColor?.shift());
      }

      chart.update();
    };
  }, []);

  return <canvas ref={chartRef} style={{ width: "100%", height: "500px" }} />;
}
