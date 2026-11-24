(function () {
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var stage = document.querySelector(".stage");
  var progress = document.querySelector(".progress");
  var live = document.querySelector(".live");
  var index = 0;
  var locked = false;

  function clamp(n) {
    if (n < 0) return 0;
    if (n > slides.length - 1) return slides.length - 1;
    return n;
  }

  function fit() {
    if (!stage) return;
    var scale = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    stage.style.transform = "scale(" + scale + ")";
  }

  function show(n) {
    index = clamp(n);
    slides.forEach(function (slide, i) {
      var on = i === index;
      slide.classList.toggle("is-active", on);
      slide.hidden = !on;
      slide.setAttribute("aria-hidden", on ? "false" : "true");
      slide.querySelectorAll(".dot").forEach(function (dot, dotIndex) {
        if (dotIndex === index) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
    });
    if (progress) progress.style.width = ((index + 1) / slides.length) * 100 + "%";
    if (live) live.textContent = slides[index].getAttribute("aria-label") || "";
    var hash = "#" + (index + 1);
    if (location.hash !== hash) history.replaceState(null, "", hash);
  }

  function start() {
    var query = new URLSearchParams(location.search).get("slide");
    var hash = /^#(\d+)$/.exec(location.hash);
    var initial = query ? Number(query) : hash ? Number(hash[1]) : 1;
    show((Number.isFinite(initial) ? initial : 1) - 1);
  }

  window.addEventListener("resize", fit);
  window.addEventListener("hashchange", function () {
    var hash = /^#(\d+)$/.exec(location.hash);
    if (hash) show(Number(hash[1]) - 1);
  });
  window.addEventListener("keydown", function (event) {
    var key = event.key;
    if (["ArrowRight", "ArrowDown", "PageDown", " "].indexOf(key) >= 0) {
      event.preventDefault();
      show(index + 1);
    } else if (["ArrowLeft", "ArrowUp", "PageUp"].indexOf(key) >= 0) {
      event.preventDefault();
      show(index - 1);
    } else if (key === "Home") {
      event.preventDefault();
      show(0);
    } else if (key === "End") {
      event.preventDefault();
      show(slides.length - 1);
    }
  });
  stage.addEventListener("click", function (event) {
    var button = event.target.closest(".dot");
    if (!button) return;
    show(Number(button.getAttribute("data-go")));
  });
  window.addEventListener("wheel", function (event) {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (locked || Math.abs(event.deltaY) < 8) return;
    event.preventDefault();
    locked = true;
    show(index + (event.deltaY > 0 ? 1 : -1));
    setTimeout(function () { locked = false; }, 700);
  }, { passive: false });

  fit();
  start();
})();
