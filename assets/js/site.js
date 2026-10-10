// El Recreo website: header shadow on scroll, reveal-on-scroll, the footer year, and the voice samples
// (playable lines, the try-it step and the Sofi vs. Rubén scene).
// Everything works without it; this only adds polish. No analytics, no cookies, no storage.
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) document.documentElement.classList.add("js");

  var bar = document.querySelector(".bar");
  function onScroll() {
    if (bar) bar.classList.toggle("scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var items = document.querySelectorAll(".reveal");
  if (document.documentElement.classList.contains("js")) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.1 });
    items.forEach(function (item) { observer.observe(item); });
  }

  var year = String(new Date().getFullYear());
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = year; });

  // ---------- Voices: one line at a time, recorded in the app's voices (assets/audio) ----------
  var current = null; // { audio, button, done }

  function stop() {
    if (!current) return;
    var was = current;
    current = null;
    was.audio.pause();
    if (was.button) {
      was.button.classList.remove("playing");
      was.button.setAttribute("aria-pressed", "false");
    }
    if (was.done) was.done(false);
  }

  // Plays assets/audio/<name>.m4a. `done(finished)` runs once, when it ends or is interrupted.
  function play(name, button, done) {
    stop();
    var audio = new Audio("assets/audio/" + name + ".m4a");
    var entry = { audio: audio, button: button, done: done };
    current = entry;
    if (button) {
      button.classList.add("playing");
      button.setAttribute("aria-pressed", "true");
    }
    function finish(ok) {
      if (current !== entry) return;
      current = null;
      if (button) {
        button.classList.remove("playing");
        button.setAttribute("aria-pressed", "false");
      }
      if (done) done(ok);
    }
    audio.addEventListener("ended", function () { finish(true); });
    audio.addEventListener("error", function () { finish(false); });
    var started = audio.play();
    if (started && started.catch) started.catch(function () { finish(false); });
  }

  function sound(name) {
    var effect = new Audio("assets/audio/" + name + ".m4a");
    effect.volume = 0.6;
    var started = effect.play();
    if (started && started.catch) started.catch(function () {});
  }

  document.querySelectorAll("[data-audio]").forEach(function (button) {
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", function () {
      if (current && current.button === button) { stop(); return; }
      play(button.getAttribute("data-audio"), button);
    });
  });

  // ---------- Try it: finish "¿Vos de dónde ___?" ----------
  var build = document.querySelector("[data-build]");
  if (build) {
    var slot = build.querySelector("[data-slot]");
    var feedback = build.querySelector("[data-feedback]");
    var meter = build.querySelector("[data-meter]");
    var again = build.querySelector("[data-again]");
    var picks = build.querySelectorAll("[data-pick]");
    var intro = feedback.innerHTML;

    picks.forEach(function (pick) {
      pick.addEventListener("click", function () {
        if (pick.getAttribute("data-pick") === "right") {
          sound("correct");
          slot.textContent = pick.textContent;
          slot.classList.add("filled");
          slot.removeAttribute("aria-hidden");
          picks.forEach(function (p) { p.disabled = true; });
          meter.style.width = "100%";
          feedback.className = "mock-note good";
          feedback.innerHTML = "¡Muy bien! <span lang=\"es\">¿Vos de dónde sos?</span> Here’s Lucho asking you the same thing.";
          again.hidden = false;
          setTimeout(function () { play("lucho-donde"); }, 650);
        } else {
          sound("incorrect");
          feedback.className = "mock-note bad";
          feedback.textContent = pick.getAttribute("data-why");
          pick.classList.remove("shake");
          void pick.offsetWidth;
          pick.classList.add("shake");
        }
      });
    });

    again.addEventListener("click", function () {
      stop();
      slot.textContent = "";
      slot.classList.remove("filled");
      slot.setAttribute("aria-hidden", "true");
      picks.forEach(function (p) { p.disabled = false; p.classList.remove("shake"); });
      meter.style.width = "64%";
      feedback.className = "mock-note";
      feedback.innerHTML = intro;
      again.hidden = true;
      picks[0].focus();
    });
  }

  // ---------- The scene: Sofi vs. Rubén, then you pick a side ----------
  var scene = document.querySelector("[data-scene]");
  if (scene) {
    var start = scene.querySelector("[data-scene-play]");
    var label = start.querySelector("span");
    var lines = Array.prototype.slice.call(scene.querySelectorAll("[data-line]"));
    var vote = scene.querySelector("[data-vote]");
    var replies = scene.querySelectorAll("[data-reply]");
    var run = 0;

    function reset() {
      scene.classList.remove("running");
      lines.forEach(function (line) { line.classList.remove("said", "now"); });
    }

    function step(i, id) {
      if (id !== run) return;
      lines.forEach(function (line) { line.classList.remove("now"); });
      if (i >= lines.length) {
        reset();
        label.textContent = "Play again";
        vote.hidden = false;
        return;
      }
      lines[i].classList.add("said", "now");
      play(lines[i].getAttribute("data-line"), null, function (finished) {
        if (!finished || id !== run) {
          if (id === run) { reset(); label.textContent = "Play the scene"; }
          return;
        }
        setTimeout(function () { step(i + 1, id); }, 350);
      });
    }

    start.addEventListener("click", function () {
      if (scene.classList.contains("running")) {
        run++;
        stop();
        reset();
        label.textContent = "Play the scene";
        return;
      }
      run++;
      vote.hidden = true;
      replies.forEach(function (reply) { reply.hidden = true; });
      scene.classList.add("running");
      label.textContent = "Stop";
      step(0, run);
    });

    scene.querySelectorAll("[data-choice]").forEach(function (choice) {
      choice.addEventListener("click", function () {
        var name = "scene-" + choice.getAttribute("data-choice");
        replies.forEach(function (reply) { reply.hidden = reply.getAttribute("data-reply") !== name; });
        play(name);
      });
    });
  }
})();
