document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.querySelector('#id_category');

    function updateEditorMode() {
        const selectedOption = categorySelect.options[categorySelect.selectedIndex];
        const mode = selectedOption.dataset.aceMode || 'text';

        const editorElement = document.querySelector('.ace_editor');

        if (editorElement && editorElement.env && editorElement.env.editor) {
            const editor = editorElement.env.editor;

            editor.session.setMode("ace/mode/" + mode);
            editor.session.setUseWorker(false);

            console.log("Editor mode switched to: " + mode);
        }
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', updateEditorMode);
        setTimeout(updateEditorMode, 500);
    }
});