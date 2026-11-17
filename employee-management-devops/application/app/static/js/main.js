// main.js - Employee Management DevOps App

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alert banners after 5 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Dynamic Chart.js Rendering for Dashboard
  const deptChartEl = document.getElementById("departmentChart");
  if (deptChartEl && window.deptLabels && window.deptCounts) {
    const ctx = deptChartEl.getContext("2d");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: window.deptLabels,
        datasets: [{
          data: window.deptCounts,
          backgroundColor: [
            "#3b82f6",
            "#10b981",
            "#f59e0b",
            "#8b5cf6",
            "#ec4899",
            "#06b6d4"
          ],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 12,
              font: { size: 12 }
            }
          }
        },
        cutout: "70%"
      }
    });
  }

  // Generic Confirmation modal trigger for delete operations
  const deleteButtons = document.querySelectorAll("[data-confirm-delete]");
  deleteButtons.forEach(button => {
    button.addEventListener("click", function(e) {
      const itemName = this.getAttribute("data-confirm-name") || "this record";
      if (!confirm(`Are you sure you want to permanently delete ${itemName}?`)) {
        e.preventDefault();
      }
    });
  });
});
