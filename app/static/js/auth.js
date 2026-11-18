/* Admin sign-in: show/hide password + Caps Lock notice. */
(function () {
  "use strict";
  document.querySelectorAll("[data-pw-toggle]").forEach(function (btn) {
    var input = document.getElementById(btn.getAttribute("aria-controls"));
    if (!input) return;
    btn.addEventListener("click", function () {
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.setAttribute("aria-pressed", show ? "true" : "false");
      btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
      input.focus();
    });
    var caps = document.getElementById(input.id + "-caps");
    if (!caps) return;
    function check(e) { if (e.getModifierState) caps.hidden = !e.getModifierState("CapsLock"); }
    input.addEventListener("keydown", check);
    input.addEventListener("keyup", check);
    input.addEventListener("blur", function () { caps.hidden = true; });
  });
})();
