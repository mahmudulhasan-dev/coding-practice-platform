(function () {
    const runButton = document.getElementById('run-sql-btn');
    if (!runButton) return;

    const container = document.getElementById('sql-runner');
    const problemId = container.dataset.problemId;
    const csrfToken = container.dataset.csrf;
    const resultsEl = document.getElementById('sql-results');
    const verdictEl = document.getElementById('sql-verdict');

    runButton.addEventListener('click', function () {
        const query = editor.getValue();
        resultsEl.innerHTML = '';
        verdictEl.innerHTML = '';
        runButton.disabled = true;
        runButton.textContent = 'Running...';

        fetch(`/problems/${problemId}/run-sql/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ query: query }),
        })
            .then((r) => r.json())
            .then((data) => {
                if (data.error) {
                    verdictEl.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error)}</div>`;
                    return;
                }
                renderResultTable(data.columns, data.rows);
                verdictEl.innerHTML = data.is_correct
                    ? '<div class="alert alert-success">Correct!</div>'
                    : '<div class="alert alert-warning">Not quite — compare your output below.</div>';
            })
            .catch(() => {
                verdictEl.innerHTML = '<div class="alert alert-danger">Something went wrong running your query.</div>';
            })
            .finally(() => {
                runButton.disabled = false;
                runButton.textContent = 'Run Query';
            });
    });

    function renderResultTable(columns, rows) {
        if (!columns || columns.length === 0) {
            resultsEl.innerHTML = '<p class="text-muted">No columns returned.</p>';
            return;
        }
        let html = '<table class="table table-dark table-striped table-sm"><thead><tr>';
        columns.forEach((col) => (html += `<th>${escapeHtml(col)}</th>`));
        html += '</tr></thead><tbody>';
        rows.forEach((row) => {
            html += '<tr>';
            row.forEach((cell) => (html += `<td>${escapeHtml(String(cell))}</td>`));
            html += '</tr>';
        });
        html += '</tbody></table>';
        resultsEl.innerHTML = html;
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
})();