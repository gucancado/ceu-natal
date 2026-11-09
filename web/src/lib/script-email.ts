// Script inline do link de e-mail: monta o mailto só no clique, sem depender da hidratação do React.
export const scriptEmail = `(function () {
  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest("[data-email-usuario]");
    if (!link) return;
    e.preventDefault();
    var assunto = link.getAttribute("data-email-assunto");
    location.href = "mailto:" + link.getAttribute("data-email-usuario") + "@" + link.getAttribute("data-email-dominio") +
      (assunto ? "?subject=" + encodeURIComponent(assunto) : "");
  });
})();`;
