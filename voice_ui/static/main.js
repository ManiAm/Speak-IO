
function showTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(tab => tab.style.display = "none");
  document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));

  document.getElementById(tabId).style.display = "block";
  document.querySelector(`.tab-button[onclick="showTab('${tabId}')"]`).classList.add("active");
}
