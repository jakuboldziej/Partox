let pagination_el = document.getElementsByClassName("right_panel_el");
let pagination_li = document.getElementsByClassName("pagination_link");

window.addEventListener('load', function(e) {
  const id = e.target.location.href.split("#")[1];
  panel = document.getElementById(id)
  panel.style.display = "flex";
  document.querySelector(`a[href='#${id}']`).classList.add("active");
  hidePanels(panel);
});

for (let i = 0; i < pagination_li.length; i++) {
  pagination_li[i].addEventListener("click", showPanel);
}

function showPanel(e) {
  const id = e.target.href.split("#")[1];
  panel = document.getElementById(id);

  panel.style.display = "flex";
  document.querySelector(`a[href='#${id}']`).classList.add("active");
  hidePanels(panel);
}

function hidePanels(panel) {
  for (let i = 0; i < pagination_el.length; i++) {
    if (pagination_el[i].id !== panel.id) {
      pagination_el[i].style.display = "none";
      document.querySelector(`a[href='#${pagination_el[i].id}']`).classList.remove("active");
    }
    // if (iter !== i) {
      // try {
        // pagination_li[i].classList.remove("active");
      // } catch {}
    }
}