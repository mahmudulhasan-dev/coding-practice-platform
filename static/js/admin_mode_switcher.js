document.addEventListener('DOMContentLoaded', function() {
    const languageSelect = document.querySelector('#id_language');

    function updateEditorMode() {
        const selectedOption = languageSelect.options[languageSelect.selectedIndex];
        const mode = selectedOption.dataset.aceMode || 'text';

        const editorElement = document.querySelector('.ace_editor');

        if (editorElement && editorElement.env && editorElement.env.editor) {
            const editor = editorElement.env.editor;

            editor.session.setMode("ace/mode/" + mode);
            editor.session.setUseWorker(false);

            console.log("Editor mode switched to: " + mode);
        }
    }

    if (languageSelect) {
        languageSelect.addEventListener('change', updateEditorMode);
        setTimeout(updateEditorMode, 500);
    }
});