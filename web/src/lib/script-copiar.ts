// Script inline da cópia. Não depende do React: o botão funciona desde a primeira pintura,
// e não só depois da hidratação, que num celular ou PC lento leva vários segundos.
// O estado fica em data-estado no invólucro e o CSS troca o rótulo (ver globals.css).
export const scriptCopiar = `(function () {
  function antigo(texto) {
    var foco = document.activeElement;
    var area = document.createElement("textarea");
    area.value = texto;
    area.readOnly = true;
    area.style.cssText = "position:fixed;top:0;left:0;opacity:0;font-size:16px";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) {}
    area.remove();
    if (foco && foco.focus) foco.focus();
    return ok;
  }
  function selecionar(id) {
    var el = id && document.getElementById(id);
    if (el) window.getSelection().selectAllChildren(el);
  }
  function marcar(caixa, botao, ok) {
    clearTimeout(caixa.__copiar);
    caixa.setAttribute("data-estado", ok ? "copiado" : "falhou");
    if (!ok) selecionar(botao.getAttribute("data-alvo"));
    caixa.__copiar = setTimeout(function () { caixa.removeAttribute("data-estado"); }, ok ? 2500 : 6000);
  }
  document.addEventListener("click", function (e) {
    var botao = e.target.closest && e.target.closest("[data-copiar]");
    if (!botao) return;
    var texto = botao.getAttribute("data-copiar");
    var caixa = botao.parentNode;
    var cb = navigator.clipboard;
    if (!cb) return marcar(caixa, botao, antigo(texto));
    cb.writeText(texto).then(
      function () { marcar(caixa, botao, true); },
      function () { marcar(caixa, botao, antigo(texto)); }
    );
  });
})();`;
