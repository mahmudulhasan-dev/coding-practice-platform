document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.querySelector('#id_category');
    const modeMapping = {
        'Python': 'python',
        'MySQL': 'mysql',
        'C++': 'c_cpp',
        'C': 'c_cpp',
        'JavaScript': 'javascript'
    };

    function updateEditorMode() {
        const selectedCategory = categorySelect.options[categorySelect.selectedIndex].text;
        const mode =  modeMapping[selectedCategory] || 'text';

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