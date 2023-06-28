let pagination_el = document.getElementsByClassName("right_panel_el");
let pagination_li = document.getElementsByClassName("pagination_link");
let left_panel = document.querySelector(".left-panel");
let canvasBtn = document.querySelector("#canvasBtn");

window.addEventListener('load', function(e) {
  let id = e.target.location.href.split("#")[1];
  if (!id) {
    id = "server-info";
  }
  
  let panel = document.getElementById(id);
  panel.style.display = "flex";
  document.querySelector(`a[href='#${id}']`).classList.add("active");
  hidePanels(panel);
});

for (let i = 0; i < pagination_li.length; i++) {
  pagination_li[i].addEventListener("click", showPanel);
}

function showPanel(e) {
  const id = e.target.href.split("#")[1];
  let panel = document.getElementById(id);

  panel.style.display = "flex";
  document.querySelector(`a[href='#${id}']`).classList.add("active");
  hidePanels(panel);

  if (left_panel.classList.contains("show")) {
    left_panel.style.display = "none";
    canvasBtn.style.marginLeft = "0";
  } else {
    left_panel.style.display = "block";
    canvasBtn.style.marginLeft = "262px";
  }
}

function hidePanels(panel) {
  for (let i = 0; i < pagination_el.length; i++) {
    if (pagination_el[i].id !== panel.id) {
      pagination_el[i].style.display = "none";
      document.querySelector(`a[href='#${pagination_el[i].id}']`).classList.remove("active");
    }
  }
}

document.getElementById("canvasBtn").addEventListener("click", function() {

  if (left_panel.style.display == "none" || left_panel.style.display == "") {
    left_panel.style.display = "block";
    left_panel.classList.add("show");
    canvasBtn.style.marginLeft = "262px";
  } else {
    left_panel.style.display = "none";
    left_panel.classList.remove("show");
    canvasBtn.style.marginLeft = "0";
  }
});