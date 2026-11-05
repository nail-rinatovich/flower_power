document.querySelectorAll('[data-dismiss]').forEach(button => button.addEventListener('click', () => button.parentElement.remove()));
document.querySelectorAll('img[data-fallback]').forEach(img => {
  const fallback = () => { if (img.dataset.fallback) { const url = img.dataset.fallback; delete img.dataset.fallback; img.src = url; } };
  img.addEventListener('error', fallback);
  if (img.complete && !img.naturalWidth) fallback();
});
document.querySelectorAll('#filters').forEach(form => form.addEventListener('submit', event => {
  if (!event.submitter || event.submitter.name !== 'category') form.querySelector('[data-category]').disabled = false;
}));
document.querySelectorAll('[data-auto-submit]').forEach(select => select.addEventListener('change', () => {
  select.form.querySelector('[data-category]').disabled = false;
  select.form.requestSubmit();
}));
