fetch(`/problems/${problemId}/run-sql/`, {method: "POST", body: formData})
  .then(r => r.json())
  .then(data => {
    if (data.error) return showError(data.error);
    renderResultTable(data.columns, data.rows);  // build <table> from JSON
    showVerdict(data.is_correct);
  });