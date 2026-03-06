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

class InventoryDashboard extends Component {
  setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    this.state = useState({
      stats: {},
      topSelling: [],
      lowStock: [],
      outOfStock: [],
      recentAdjustments: [],
    });

    this.adjustmentsChartRef = useRef("adjustmentsChart");
    this._adjustmentsChart = null;

    onWillStart(async () => {
      const [dashboard] = await this.orm.searchRead(
        "inventory.dashboard",
        [],
        [
          "total_products",
          "total_stock_value",
          "total_low_stock",
          "total_out_of_stock",
        ],
        { limit: 1 },
      );
      this.state.stats = dashboard || {};

      this.state.topSelling = await this.orm.searchRead(
        "inventory.products",
        [["total_revenue", ">", 0]],
        ["product_name", "total_sold", "stock", "price", "total_revenue"],
        { order: "total_revenue desc", limit: 10 },
      );

      this.state.lowStock = await this.orm.searchRead(
        "inventory.products",
        [["status", "=", "low_stock"]],
        ["product_name", "stock", "min_stock", "price"],
      );

      this.state.outOfStock = await this.orm.searchRead(
        "inventory.products",
        [["status", "=", "out_of_stock"]],
        ["product_name", "stock", "min_stock", "price"],
      );

      this.state.recentAdjustments = await this.orm.searchRead(
        "inventory.adjustments",
        [],
        ["date", "product_id", "type", "units", "reason"],
        { order: "date desc", limit: 5 },
      );

      this._adjRaw = await this.orm.searchRead(
        "inventory.adjustments",
        [],
        ["date", "type", "units"],
        { order: "date asc" },
      );

      await loadBundle("web.chartjs_lib");
    });

    onMounted(() => this._initCharts());

    onWillUnmount(() => {
      this._adjustmentsChart?.destroy();
    });
  }

  _initCharts() {
    const Chart = window.Chart;
    const months = {};
    for (const a of this._adjRaw) {
      if (!a.date) continue;
      const d = new Date(a.date.replace(" ", "T") + "Z");
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
      if (!months[key]) months[key] = { incoming: 0, outgoing: 0 };
      if (a.type === "incoming") months[key].incoming += a.units;
      else if (a.type === "outgoing") months[key].outgoing += a.units;
    }

    const keys = Object.keys(months).sort();
    const labels = keys.map((k) => {
      const [year, month] = k.split("-");
      return new Date(Number(year), Number(month) - 1).toLocaleString("en-US", {
        month: "short",
        year: "numeric",
      });
    });

    this._adjustmentsChart = new Chart(this.adjustmentsChartRef.el, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Incoming",
            data: keys.map((k) => months[k].incoming),
            backgroundColor: "rgba(75, 192, 192, 0.5)",
            borderRadius: 5,
          },
          {
            label: "Outgoing",
            data: keys.map((k) => months[k].outgoing),
            backgroundColor: "rgba(255, 99, 132, 0.5)",
            borderRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#a6adc8" } },
        },
        scales: {
          x: { ticks: { color: "#a6adc8" }, grid: { color: "#313244" } },
          y: {
            ticks: { color: "#a6adc8" },
            grid: { color: "#313244" },
            beginAtZero: true,
          },
        },
      },
    });
  }

  openRecord = (model, id) => {
    this.action.doAction({
      type: "ir.actions.act_window",
      res_model: model,
      res_id: id,
      views: [[false, "form"]],
      target: "current",
    });
  };

  formatDate(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr.replace(" ", "T") + "Z");
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }
}

InventoryDashboard.template = "inventory.Dashboard";

registry.category("actions").add("inventory.Dashboard", InventoryDashboard);
