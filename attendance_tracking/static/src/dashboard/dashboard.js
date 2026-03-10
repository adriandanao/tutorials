/** @odoo-module **/

import { registry } from "@web/core/registry";
import {
  Component,
  useState,
  onWillStart,
  useRef,
  onMounted,
  onWillUnmount,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";

class AttendanceDashboard extends Component {
  static template = "attendance_tracking.Dashboard";

  setup() {
    this.orm = useService("orm");
    this.state = useState({
      stats: {},
      todayAttendance: [],
    });

    this.weeklyChartRef = useRef("weeklyChart");
    this._weeklyChart = null;
    this._weeklyData = [];

    onWillStart(async () => {
      const data = await this.orm.call(
        "attendance_tracking.dashboard",
        "get_dashboard_data",
        [],
      );
      this.state.stats = data;
      this._weeklyData = data.weekly_data || [];

      const now = new Date();
      const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
      this.state.todayAttendance = await this.orm.searchRead(
        "attendance_tracking.attendance",
        [["date", "=", today]],
        ["student_id", "time_in", "time_out", "status"],
        { order: "time_in asc" },
      );

      await loadBundle("web.chartjs_lib");
    });

    onMounted(() => this._initChart());
    onWillUnmount(() => {
      this._weeklyChart?.destroy();
    });
  }

  _initChart() {
    const Chart = window.Chart;
    const labels = this._weeklyData.map((d) => d.date);
    const values = this._weeklyData.map((d) => d.present);
    const total = this.state.stats.total_students || 10;

    this._weeklyChart = new Chart(this.weeklyChartRef.el, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Students Present",
            data: values,
            backgroundColor: "rgba(137, 180, 250, 0.6)",
            borderColor: "rgba(137, 180, 250, 1)",
            borderWidth: 1,
            borderRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#cdd6f4" } },
        },
        scales: {
          x: { ticks: { color: "#a6adc8" }, grid: { color: "#313244" } },
          y: {
            ticks: { color: "#a6adc8" },
            grid: { color: "#313244" },
            beginAtZero: true,
            max: total,
          },
        },
      },
    });
  }

  formatTime(datetimeStr) {
    if (!datetimeStr) return "-";
    const d = new Date(datetimeStr.replace(" ", "T") + "Z");
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
}

registry.category("actions").add("attendance.Dashboard", AttendanceDashboard);
