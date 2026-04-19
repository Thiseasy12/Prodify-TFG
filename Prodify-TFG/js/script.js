var i18n = (function () {
    var el = document.getElementById('i18nData');
    if (!el) return {};
    try { return JSON.parse(el.textContent); } catch (_) { return {}; }
}());

function t(key, fallback) {
    return i18n[key] !== undefined ? i18n[key] : fallback;
}

function getSwalTheme() {
    const isLight = document.body.classList.contains('theme-light');
    return {
        confirmButtonColor: '#2f63ff',
        background: isLight ? '#f4f8ff' : '#0c1629',
        color: isLight ? '#14305f' : '#e6eeff',
    };
}

document.addEventListener('DOMContentLoaded', function () {
    /*
     * Cojo los elementos principales cuando ya se ha cargado el DOM.
     */
    const body = document.body;
    const themeButton = document.getElementById('themeToggle');
    const savedTheme = window.localStorage.getItem('prodify-theme');
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

    if (csrfToken) {
        const postForms = document.querySelectorAll('form[method="POST"], form[method="post"]');
        for (let f = 0; f < postForms.length; f += 1) {
            if (postForms[f].querySelector('input[name="csrf_token"]')) continue;
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'csrf_token';
            tokenInput.value = csrfToken;
            postForms[f].appendChild(tokenInput);
        }
    }

    const languageForms = document.querySelectorAll('.js-language-form');
    for (let lf = 0; lf < languageForms.length; lf += 1) {
        const form = languageForms[lf];
        const dropdown = form.querySelector('.js-language-dropdown');
        const trigger = form.querySelector('.js-language-trigger');
        const menu = form.querySelector('.topbar-language-menu');
        const hiddenInput = form.querySelector('input[name="preferred_language"]');
        const options = form.querySelectorAll('.js-language-option');

        if (!dropdown || !trigger || !menu || !hiddenInput || !options.length) continue;

        trigger.addEventListener('click', function () {
            const isOpen = !menu.hasAttribute('hidden');
            const allMenus = document.querySelectorAll('.topbar-language-menu');
            const allTriggers = document.querySelectorAll('.js-language-trigger');

            for (let index = 0; index < allMenus.length; index += 1) {
                allMenus[index].setAttribute('hidden', 'hidden');
            }
            for (let index = 0; index < allTriggers.length; index += 1) {
                allTriggers[index].setAttribute('aria-expanded', 'false');
            }

            if (!isOpen) {
                menu.removeAttribute('hidden');
                trigger.setAttribute('aria-expanded', 'true');
            }
        });

        for (let optionIndex = 0; optionIndex < options.length; optionIndex += 1) {
            options[optionIndex].addEventListener('click', function () {
                const selectedValue = this.getAttribute('data-language-value') || '';
                if (!selectedValue || selectedValue === hiddenInput.value) {
                    menu.setAttribute('hidden', 'hidden');
                    trigger.setAttribute('aria-expanded', 'false');
                    return;
                }
                hiddenInput.value = selectedValue;
                form.submit();
            });
        }
    }

    document.addEventListener('click', function (event) {
        for (let lf = 0; lf < languageForms.length; lf += 1) {
            const form = languageForms[lf];
            const dropdown = form.querySelector('.js-language-dropdown');
            const trigger = form.querySelector('.js-language-trigger');
            const menu = form.querySelector('.topbar-language-menu');
            if (!dropdown || !trigger || !menu) continue;
            if (!dropdown.contains(event.target)) {
                menu.setAttribute('hidden', 'hidden');
                trigger.setAttribute('aria-expanded', 'false');
            }
        }
    });

    /*
     * Si el usuario habia guardado el tema claro, lo aplico al entrar.
     */
    if (savedTheme === 'light') {
        body.classList.add('theme-light');
    }

    /*
     * Cambio el icono del boton segun el tema activo.
     */
    const themeToggleLabels = {
        es: { dark: 'Activar modo oscuro', light: 'Activar modo claro' },
        en: { dark: 'Turn on dark mode', light: 'Turn on light mode' },
        fr: { dark: 'Activer le mode sombre', light: 'Activer le mode clair' },
        de: { dark: 'Dunklen Modus aktivieren', light: 'Hellen Modus aktivieren' },
        it: { dark: 'Attiva la modalita scura', light: 'Attiva la modalita chiara' }
    };

    function getThemeLabels() {
        const htmlLang = (document.documentElement.getAttribute('lang') || 'es').trim();
        return themeToggleLabels[htmlLang] || themeToggleLabels[htmlLang.split('-')[0]] || themeToggleLabels.es;
    }

    function updateThemeText() {
        if (!themeButton) return;
        const labels = getThemeLabels();
        if (body.classList.contains('theme-light')) {
            themeButton.textContent = '☀';
            themeButton.setAttribute('aria-label', labels.dark);
        } else {
            themeButton.textContent = '🌙';
            themeButton.setAttribute('aria-label', labels.light);
        }
    }

    if (themeButton) {
        updateThemeText();
        themeButton.addEventListener('click', function () {
            /*
             * Alterno el tema y lo guardo para futuras visitas.
             */
            body.classList.toggle('theme-light');
            if (body.classList.contains('theme-light')) {
                window.localStorage.setItem('prodify-theme', 'light');
            } else {
                window.localStorage.setItem('prodify-theme', 'dark');
            }
            updateThemeText();
        });
    }

    /*
     * Si hay un mensaje pendiente, lo muestro con SweetAlert.
     */
    const pendingToast = window.sessionStorage.getItem('prodify-toast');
    if (pendingToast && window.Swal) {
        window.sessionStorage.removeItem('prodify-toast');
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: pendingToast,
            showConfirmButton: false,
            timer: 1800,
            timerProgressBar: true,
        });
    }

    /*
     * Esto controla el menu desplegable de la cuenta.
     */
    const accountButton = document.getElementById('accountToggle');
    const accountMenu = document.getElementById('accountMenu');
    if (accountButton && accountMenu) {
        accountButton.addEventListener('click', function () {
            if (accountMenu.hasAttribute('hidden')) {
                accountMenu.removeAttribute('hidden');
            } else {
                accountMenu.setAttribute('hidden', 'hidden');
            }
        });

        document.addEventListener('click', function (event) {
            /*
             * Si el click es fuera, cierro el menu.
             */
            if (!accountMenu.contains(event.target) && !accountButton.contains(event.target)) {
                accountMenu.setAttribute('hidden', 'hidden');
            }
        });
    }

    const avatarFileInput = document.getElementById('avatarFileInput');
    const avatarPickerButton = document.querySelector('.js-avatar-picker');
    const avatarFileName = document.getElementById('avatarFileName');

    if (avatarFileInput && avatarPickerButton) {
        avatarPickerButton.addEventListener('click', function () {
            avatarFileInput.click();
        });

        avatarFileInput.addEventListener('change', function () {
            if (!avatarFileName) return;
            const file = this.files && this.files[0] ? this.files[0].name : '';
            avatarFileName.textContent = file || 'Ningún archivo seleccionado';
        });
    }

    function parseJsonScript(id) {
        const element = document.getElementById(id);
        if (!element || !element.textContent) return [];
        try {
            return JSON.parse(element.textContent);
        } catch (_error) {
            return [];
        }
    }

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    const createWorkspaceButton = document.querySelector('.js-create-workspace');
    const createDropdown = document.getElementById('createDropdown');
    const createBoardOption = document.querySelector('.js-create-board-option');
    const createTemplateOption = document.querySelector('.js-create-template-option');
    const workspaceForm = document.getElementById('workspaceCreateForm');
    const workspaceNameInput = document.getElementById('workspaceNameInput');
    const workspaceBoardNameInput = document.getElementById('workspaceBoardNameInput');
    const boardForm = document.getElementById('boardCreateForm');
    const boardNameInput = document.getElementById('boardNameInput');
    const createBoardCards = document.querySelectorAll('.js-create-board');
    const templateButtons = document.querySelectorAll('.js-use-template');
    const templateForm = document.getElementById('templateCreateForm');
    const templateWorkspaceInput = document.getElementById('templateWorkspaceInput');
    const templateWorkspaceIdInput = document.getElementById('templateWorkspaceIdInput');
    const templateBoardInput = document.getElementById('templateBoardInput');
    const templateIdInput = document.getElementById('templateIdInput');
    const creationWorkspaces = parseJsonScript('boardCreationWorkspaces');
    const creationTemplates = parseJsonScript('boardCreationTemplates');

    function getTemplateById(templateId) {
        for (let i = 0; i < creationTemplates.length; i += 1) {
            if (creationTemplates[i].id === templateId) return creationTemplates[i];
        }
        return creationTemplates[0] || null;
    }

    function buildWorkspaceOptions(selectedWorkspaceId) {
        const options = ['<option value="">' + t('js.select_workspace', 'Selecciona un espacio') + '</option>'];
        for (let i = 0; i < creationWorkspaces.length; i += 1) {
            const workspace = creationWorkspaces[i];
            const selected = String(selectedWorkspaceId || '') === String(workspace.id) ? ' selected' : '';
            options.push('<option value="' + escapeHtml(workspace.id) + '"' + selected + '>' + escapeHtml(workspace.name) + '</option>');
        }
        options.push('<option value="__new__">' + t('js.create_new_workspace', 'Crear espacio nuevo') + '</option>');
        return options.join('');
    }

    function buildTemplatePicker(selectedTemplateId) {
        if (!creationTemplates.length) {
            return '<div class="board-creator-empty">' + t('js.no_templates', 'No hay plantillas disponibles todav\u00eda.') + '</div>';
        }

        const cards = [];
        for (let i = 0; i < Math.min(6, creationTemplates.length); i += 1) {
            const template = creationTemplates[i];
            const active = template.id === selectedTemplateId ? ' is-active' : '';
            cards.push(
                '<button type="button" class="board-template-option' + active + '" data-template-option="' + escapeHtml(template.id) + '">' +
                    '<strong>' + escapeHtml(template.name) + '</strong>' +
                    '<span>' + escapeHtml(template.category) + '</span>' +
                '</button>'
            );
        }
        return cards.join('');
    }

    function buildPreviewColumns(template) {
        const columns = template && template.columns ? template.columns.slice(0, 3) : [t('js.col_pending', 'Pendiente'), t('js.col_in_progress', 'En curso'), t('js.col_done', 'Listo')];
        const items = [];
        for (let i = 0; i < columns.length; i += 1) {
            items.push(
                '<div class="board-creator-col">' +
                    '<span class="board-creator-col-title">' + escapeHtml(columns[i]) + '</span>' +
                    '<i></i><i></i><i></i>' +
                '</div>'
            );
        }
        return items.join('');
    }

    function applyPreviewBackground(previewShell, colorValue, fileInput) {
        if (!previewShell) return;
        const selectedFile = fileInput && fileInput.files && fileInput.files[0] ? fileInput.files[0] : null;
        if (selectedFile) {
            const objectUrl = URL.createObjectURL(selectedFile);
            previewShell.style.backgroundImage = 'linear-gradient(rgba(6, 10, 18, .18), rgba(6, 10, 18, .28)), url("' + objectUrl + '")';
            previewShell.style.backgroundSize = 'cover';
            previewShell.style.backgroundPosition = 'center';
            return;
        }
        previewShell.style.backgroundImage = 'none';
        previewShell.style.background = colorValue || '';
    }

    function updateBoardCreationPreview(popup, mode, selectedTemplateId) {
        const preview = popup.querySelector('[data-board-preview]');
        const summary = popup.querySelector('[data-template-summary]');
        const pickerWrap = popup.querySelector('[data-template-wrap]');
        const confirmButton = Swal.getConfirmButton();
        const template = getTemplateById(selectedTemplateId);
        const appearanceWrap = popup.querySelector('[data-appearance-wrap]');
        const activeColor = popup.querySelector('.board-color-option.is-active');
        const colorValue = activeColor ? activeColor.getAttribute('data-color-value') : '';
        const fileInput = popup.querySelector('#swal-board-cover');
        const previewShell = popup.querySelector('.board-creator-preview-shell');

        if (preview) {
            preview.innerHTML = buildPreviewColumns(mode === 'template' ? template : null);
        }
        if (summary) {
            summary.textContent = mode === 'template' && template
                ? template.summary
                : t('js.empty_board_summary', 'Crea un tablero vacio con la estructura base y personalizalo despues.');
        }
        if (pickerWrap) {
            pickerWrap.hidden = mode !== 'template';
        }
        if (appearanceWrap) {
            appearanceWrap.hidden = mode !== 'normal';
        }
        if (confirmButton) {
            confirmButton.textContent = mode === 'template' ? t('js.create_board_with_template', 'Crear tablero con plantilla') : t('js.create_board', 'Crear tablero');
        }
        applyPreviewBackground(previewShell, mode === 'normal' ? colorValue : '', mode === 'normal' ? fileInput : null);
    }

    function updateWorkspaceField(popup) {
        const workspaceSelect = popup.querySelector('#swal-board-workspace');
        const newWorkspaceField = popup.querySelector('[data-new-workspace-field]');
        if (!workspaceSelect || !newWorkspaceField) return;
        newWorkspaceField.hidden = workspaceSelect.value !== '__new__';
    }

    function openBoardCreationModal(config) {
        if (!window.Swal || !workspaceForm || !workspaceNameInput || !workspaceBoardNameInput || !boardForm || !boardNameInput || !templateForm || !templateWorkspaceInput || !templateWorkspaceIdInput || !templateBoardInput || !templateIdInput) {
            return;
        }

        const initialMode = config.mode === 'template' ? 'template' : 'normal';
        const lockMode = !!config.lockMode;
        const initialWorkspaceId = config.workspaceId ? String(config.workspaceId) : '';
        const initialWorkspaceName = config.workspaceName || '';
        const initialBoardName = config.boardName || '';
        const initialTemplate = getTemplateById(config.templateId) || getTemplateById('');
        const initialTemplateId = initialTemplate ? initialTemplate.id : '';

        Swal.fire({
            title: initialMode === 'template' ? t('js.create_board_with_template', 'Crear tablero con plantilla') : t('js.create_board', 'Crear tablero'),
            width: 620,
            showCancelButton: true,
            cancelButtonText: t('js.cancel', 'Cancelar'),
            confirmButtonText: initialMode === 'template' ? t('js.create_board_with_template', 'Crear tablero con plantilla') : t('js.create_board', 'Crear tablero'),
            ...getSwalTheme(),
            customClass: {
                popup: 'board-creator-modal',
                htmlContainer: 'board-creator-body-wrap',
                confirmButton: 'board-creator-confirm',
                cancelButton: 'board-creator-cancel',
            },
            html:
                '<div class="board-creator-body">' +
                    (lockMode ? '' :
                        '<div class="board-creator-mode">' +
                            '<button type="button" class="board-mode-btn' + (initialMode === 'normal' ? ' is-active' : '') + '" data-mode="normal">' + t('js.create_normal', 'Crear normal') + '</button>' +
                            '<button type="button" class="board-mode-btn' + (initialMode === 'template' ? ' is-active' : '') + '" data-mode="template">' + t('js.use_template', 'Usar plantilla') + '</button>' +
                        '</div>'
                    ) +
                    '<div class="board-creator-preview-shell">' +
                        '<div class="board-creator-preview-top"><span>' + t('js.preview', 'Vista previa') + '</span><span class="board-creator-preview-icon"></span></div>' +
                        '<div class="board-creator-preview" data-board-preview></div>' +
                    '</div>' +
                    '<div class="board-creator-template-copy" data-template-summary></div>' +
                    '<div class="board-creator-appearance" data-appearance-wrap' + (initialMode === 'normal' ? '' : ' hidden') + '>' +
                        '<div class="board-creator-field board-creator-field-tight"><label>' + t('js.board_background', 'Fondo del tablero') + '</label></div>' +
                        '<div class="board-color-grid">' +
                            '<button type="button" class="board-color-option is-active" data-color-value="#1d4ed8" style="background:#1d4ed8"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#0f766e" style="background:#0f766e"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#be185d" style="background:#be185d"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#7c3aed" style="background:#7c3aed"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#ea580c" style="background:#ea580c"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#334155" style="background:#334155"></button>' +
                        '</div>' +
                        '<div class="board-cover-upload">' +
                            '<label for="swal-board-cover" class="board-cover-upload-btn">' + t('js.upload_image', 'Subir imagen') + '</label>' +
                            '<input id="swal-board-cover" type="file" accept=".jpg,.jpeg,.png,.svg,.webp,image/jpeg,image/png,image/svg+xml,image/webp">' +
                            '<span class="board-cover-upload-name" id="swal-board-cover-name">' + t('js.no_file_selected', 'Ning\u00FAn archivo seleccionado') + '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="board-creator-field">' +
                        '<label for="swal-board-title">' + t('js.board_title', 'Titulo del tablero') + '</label>' +
                        '<input id="swal-board-title" class="swal2-input board-creator-input" value="' + escapeHtml(initialBoardName) + '" placeholder="' + t('js.board_title_placeholder', 'Ej. Sprint de abril') + '">' +
                    '</div>' +
                    '<div class="board-creator-field">' +
                        '<label for="swal-board-workspace">' + t('js.workspace', 'Espacio de trabajo') + '</label>' +
                        '<select id="swal-board-workspace" class="swal2-select board-creator-select">' + buildWorkspaceOptions(initialWorkspaceId) + '</select>' +
                    '</div>' +
                    '<div class="board-creator-field" data-new-workspace-field hidden>' +
                        '<label for="swal-new-workspace">' + t('js.new_workspace_name', 'Nombre del nuevo espacio') + '</label>' +
                        '<input id="swal-new-workspace" class="swal2-input board-creator-input" value="' + escapeHtml(initialWorkspaceName) + '" placeholder="' + t('js.new_workspace_placeholder', 'Ej. Producto Q2') + '">' +
                    '</div>' +
                    '<div class="board-creator-template-wrap" data-template-wrap' + (initialMode === 'template' ? '' : ' hidden') + '>' +
                        '<div class="board-creator-field board-creator-field-tight"><label>' + t('js.template', 'Plantilla') + '</label></div>' +
                        '<div class="board-template-grid">' + buildTemplatePicker(initialTemplateId) + '</div>' +
                    '</div>' +
                '</div>',
            didOpen: function (popup) {
                let currentMode = initialMode;
                let currentTemplateId = initialTemplateId;
                const modeButtons = popup.querySelectorAll('[data-mode]');
                const workspaceSelect = popup.querySelector('#swal-board-workspace');
                const modalTemplateButtons = popup.querySelectorAll('[data-template-option]');
                const colorButtons = popup.querySelectorAll('.board-color-option');
                const coverInput = popup.querySelector('#swal-board-cover');
                const coverName = popup.querySelector('#swal-board-cover-name');

                updateWorkspaceField(popup);
                updateBoardCreationPreview(popup, currentMode, currentTemplateId);

                if (!lockMode) {
                    for (let i = 0; i < modeButtons.length; i += 1) {
                        modeButtons[i].addEventListener('click', function () {
                            currentMode = this.getAttribute('data-mode') || 'normal';
                            for (let j = 0; j < modeButtons.length; j += 1) {
                                modeButtons[j].classList.toggle('is-active', modeButtons[j] === this);
                            }
                            updateBoardCreationPreview(popup, currentMode, currentTemplateId);
                        });
                    }
                }

                if (workspaceSelect) {
                    workspaceSelect.addEventListener('change', function () {
                        updateWorkspaceField(popup);
                    });
                }

                for (let i = 0; i < modalTemplateButtons.length; i += 1) {
                    modalTemplateButtons[i].addEventListener('click', function () {
                        currentTemplateId = this.getAttribute('data-template-option') || '';
                        for (let j = 0; j < modalTemplateButtons.length; j += 1) {
                            modalTemplateButtons[j].classList.toggle('is-active', modalTemplateButtons[j] === this);
                        }
                        updateBoardCreationPreview(popup, currentMode, currentTemplateId);
                    });
                }

                for (let i = 0; i < colorButtons.length; i += 1) {
                    colorButtons[i].addEventListener('click', function () {
                        for (let j = 0; j < colorButtons.length; j += 1) {
                            colorButtons[j].classList.toggle('is-active', colorButtons[j] === this);
                        }
                        updateBoardCreationPreview(popup, currentMode, currentTemplateId);
                    });
                }

                if (coverInput) {
                    coverInput.addEventListener('change', function () {
                        if (coverName) {
                            coverName.textContent = this.files && this.files[0] ? this.files[0].name : t('js.no_file_selected', 'Ning\u00FAn archivo seleccionado');
                        }
                        updateBoardCreationPreview(popup, currentMode, currentTemplateId);
                    });
                }
            },
            preConfirm: function () {
                const popup = Swal.getPopup();
                const boardTitle = popup.querySelector('#swal-board-title').value.trim();
                const workspaceValue = popup.querySelector('#swal-board-workspace').value;
                const newWorkspaceName = popup.querySelector('#swal-new-workspace').value.trim();
                const activeModeButton = popup.querySelector('.board-mode-btn.is-active');
                const activeTemplateButton = popup.querySelector('.board-template-option.is-active');
                const activeColorButton = popup.querySelector('.board-color-option.is-active');
                const coverInput = popup.querySelector('#swal-board-cover');
                const mode = lockMode ? initialMode : (activeModeButton ? activeModeButton.getAttribute('data-mode') : 'normal');
                const templateId = activeTemplateButton ? activeTemplateButton.getAttribute('data-template-option') : initialTemplateId;
                const backgroundColor = activeColorButton ? activeColorButton.getAttribute('data-color-value') : '#1d4ed8';
                const coverFile = coverInput && coverInput.files && coverInput.files[0] ? coverInput.files[0] : null;

                if (!boardTitle) {
                    Swal.showValidationMessage(t('js.board_title_required', 'Es necesario indicar el titulo del tablero'));
                    return false;
                }
                if (!workspaceValue) {
                    Swal.showValidationMessage(t('js.workspace_required', 'Selecciona un espacio de trabajo o crea uno nuevo'));
                    return false;
                }
                if (workspaceValue === '__new__' && !newWorkspaceName) {
                    Swal.showValidationMessage(t('js.new_workspace_required', 'Escribe el nombre del nuevo espacio'));
                    return false;
                }
                if (mode === 'template' && !templateId) {
                    Swal.showValidationMessage(t('js.template_required', 'Selecciona una plantilla para continuar'));
                    return false;
                }

                return {
                    mode: mode,
                    boardTitle: boardTitle,
                    workspaceValue: workspaceValue,
                    newWorkspaceName: newWorkspaceName,
                    templateId: templateId,
                    backgroundColor: backgroundColor,
                    coverFile: coverFile,
                };
            },
        }).then(function (result) {
            if (!result.isConfirmed) return;
            const value = result.value;

            if (value.mode === 'template') {
                templateBoardInput.value = value.boardTitle;
                templateIdInput.value = value.templateId || '';
                if (value.workspaceValue === '__new__') {
                    templateWorkspaceInput.value = value.newWorkspaceName;
                    templateWorkspaceIdInput.value = '';
                } else {
                    templateWorkspaceInput.value = '';
                    templateWorkspaceIdInput.value = value.workspaceValue;
                }
                window.sessionStorage.setItem('prodify-toast', t('js.board_created_from_template', 'Tablero creado desde plantilla'));
                templateForm.submit();
                return;
            }

            const formData = new FormData();
            formData.append('csrf_token', csrfToken);
            formData.append('board_name', value.boardTitle);
            formData.append('board_background', value.backgroundColor || '#1d4ed8');
            if (value.coverFile) {
                formData.append('board_cover_file', value.coverFile);
            }

            let endpoint = '';
            let successToast = t('js.board_created', 'Tablero creado correctamente');
            if (value.workspaceValue === '__new__') {
                formData.append('workspace_name', value.newWorkspaceName);
                endpoint = '/workspaces/create';
                successToast = t('js.workspace_and_board_created', 'Espacio y tablero creados correctamente');
            } else {
                endpoint = '/workspaces/' + value.workspaceValue + '/boards/create';
            }

            fetch(endpoint, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRF-Token': csrfToken,
                    'X-Requested-With': 'fetch',
                },
            }).then(function (response) {
                if (!response.ok) throw new Error(t('js.create_board_failed_title', 'No se pudo crear el tablero'));
                return response.json();
            }).then(function (data) {
                window.sessionStorage.setItem('prodify-toast', successToast);
                if (data && data.redirect_url) {
                    window.location.href = data.redirect_url;
                    return;
                }
                window.location.reload();
            }).catch(function () {
                if (!window.Swal) return;
                Swal.fire({
                    icon: 'error',
                    title: t('js.create_board_failed_title', 'No se pudo crear el tablero'),
                    text: t('js.create_board_failed_text', 'Revisa la imagen elegida o vuelve a intentarlo.'),
                    ...getSwalTheme(),
                });
            });
        });
    }

    function closeCreateDropdown() {
        if (!createDropdown || !createWorkspaceButton) return;
        createDropdown.setAttribute('hidden', 'hidden');
        createWorkspaceButton.setAttribute('aria-expanded', 'false');
    }

    if (createWorkspaceButton && createDropdown) {
        createWorkspaceButton.addEventListener('click', function () {
            if (createDropdown.hasAttribute('hidden')) {
                createDropdown.removeAttribute('hidden');
                createWorkspaceButton.setAttribute('aria-expanded', 'true');
            } else {
                closeCreateDropdown();
            }
        });

        document.addEventListener('click', function (event) {
            if (!createDropdown.contains(event.target) && !createWorkspaceButton.contains(event.target)) {
                closeCreateDropdown();
            }
        });
    }

    if (createBoardOption) {
        createBoardOption.addEventListener('click', function () {
            closeCreateDropdown();
            openBoardCreationModal({ mode: 'normal', lockMode: true });
        });
    }

    if (createTemplateOption) {
        createTemplateOption.addEventListener('click', function () {
            closeCreateDropdown();
            openBoardCreationModal({ mode: 'template', lockMode: true });
        });
    }

    if (createBoardCards.length) {
        for (let i = 0; i < createBoardCards.length; i += 1) {
            createBoardCards[i].addEventListener('click', function () {
                openBoardCreationModal({
                    mode: 'normal',
                    workspaceId: this.getAttribute('data-workspace-id') || '',
                    workspaceName: this.getAttribute('data-workspace-name') || '',
                });
            });
        }
    }

    const workspaceUpdateForm = document.getElementById('workspaceUpdateForm');
    const workspaceUpdateNameInput = document.getElementById('workspaceUpdateNameInput');
    const workspaceSettingsButtons = document.querySelectorAll('.js-workspace-settings');

    if (workspaceSettingsButtons.length && workspaceUpdateForm && workspaceUpdateNameInput) {
        for (let s = 0; s < workspaceSettingsButtons.length; s += 1) {
            workspaceSettingsButtons[s].addEventListener('click', function () {
                if (!window.Swal) return;

                const workspaceId = this.getAttribute('data-workspace-id');
                const workspaceName = this.getAttribute('data-workspace-name') || '';
                if (!workspaceId) return;

                Swal.fire({
                    title: t('js.workspace_settings_title', 'Configuracion del espacio'),
                    input: 'text',
                    inputLabel: t('js.workspace_name', 'Nombre del espacio'),
                    inputValue: workspaceName,
                    inputPlaceholder: t('js.workspace_name_placeholder', 'Ej. Producto y roadmap'),
                    confirmButtonText: t('js.save_changes', 'Guardar cambios'),
                    showCancelButton: true,
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    ...getSwalTheme(),
                    inputValidator: function (value) {
                        if (!value || !value.trim()) return t('js.field_required', 'El nombre es obligatorio');
                        return undefined;
                    },
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    workspaceUpdateForm.action = '/workspaces/' + workspaceId + '/update';
                    workspaceUpdateNameInput.value = result.value.trim();
                    window.sessionStorage.setItem('prodify-toast', t('js.workspace_updated', 'Espacio actualizado correctamente'));
                    workspaceUpdateForm.submit();
                });
            });
        }
    }

    if (templateButtons.length) {
        /*
         * Esto sirve para crear un tablero a partir de una plantilla.
         */
        for (let t = 0; t < templateButtons.length; t += 1) {
            templateButtons[t].addEventListener('click', function () {
                const templateName = this.getAttribute('data-template-name') || 'Nuevo tablero';
                const templateId = this.getAttribute('data-template-id') || '';
                openBoardCreationModal({
                    mode: 'template',
                    boardName: templateName,
                    templateId: templateId,
                });
            });
        }
    }

    const accountUpdateEmailButton = document.querySelector('.js-account-update-email');
    const accountEmailForm = document.getElementById('accountEmailForm');
    const accountEmailInput = document.getElementById('accountEmailInput');

    if (accountUpdateEmailButton && accountEmailForm && accountEmailInput) {
        accountUpdateEmailButton.addEventListener('click', function () {
            if (!window.Swal) return;
            const currentEmail = this.getAttribute('data-current-email') || '';

            Swal.fire({
                title: t('js.update_email_title', 'Actualizar email'),
                input: 'email',
                inputLabel: t('js.update_email_label', 'Nuevo correo electronico'),
                inputValue: currentEmail,
                inputPlaceholder: t('js.update_email_placeholder', 'correo@ejemplo.com'),
                confirmButtonText: t('js.save_email', 'Guardar email'),
                showCancelButton: true,
                cancelButtonText: t('js.cancel', 'Cancelar'),
                ...getSwalTheme(),
                inputValidator: function (value) {
                    if (!value || !value.trim()) return t('js.email_required', 'Introduce un correo electronico');
                    const emailValue = value.trim();
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailPattern.test(emailValue)) return t('js.email_invalid', 'Introduce un correo electronico valido');
                    return undefined;
                },
            }).then(function (result) {
                if (!result.isConfirmed) return;
                accountEmailInput.value = result.value.trim();
                accountEmailForm.submit();
            });
        });
    }

    /*
     * Formulario para crear columnas.
     */
    const addColumnButton = document.querySelector('.js-add-column');
    const columnForm = document.getElementById('columnCreateForm');
    const columnTitleInput = document.getElementById('columnTitleInput');
    const columnUpdateForm = document.getElementById('columnUpdateForm');
    const columnUpdateTitleInput = document.getElementById('columnUpdateTitleInput');
    const editColumnButtons = document.querySelectorAll('.js-edit-column');

    if (addColumnButton && columnForm && columnTitleInput) {
        addColumnButton.addEventListener('click', function () {
            if (!window.Swal) return;
            Swal.fire({
                title: t('js.new_column_title', 'Nueva columna'),
                input: 'text',
                inputLabel: t('js.column_name', 'Nombre de la columna'),
                inputPlaceholder: t('js.column_placeholder', 'Ej. En revision'),
                showCancelButton: true,
                confirmButtonText: t('js.create', 'Crear'),
                cancelButtonText: t('js.cancel', 'Cancelar'),
                ...getSwalTheme(),
                inputValidator: function (value) {
                    if (!value || !value.trim()) return t('js.field_required', 'El nombre es obligatorio');
                    return undefined;
                },
            }).then(function (result) {
                if (!result.isConfirmed) return;
                columnTitleInput.value = result.value.trim();
                columnForm.submit();
            });
        });
    }

    if (editColumnButtons.length && columnUpdateForm && columnUpdateTitleInput) {
        for (let columnIndex = 0; columnIndex < editColumnButtons.length; columnIndex += 1) {
            editColumnButtons[columnIndex].addEventListener('click', function () {
                if (!window.Swal) return;
                const columnId = this.getAttribute('data-column-id');
                const currentTitle = this.getAttribute('data-column-title') || '';
                if (!columnId) return;

                Swal.fire({
                    title: t('js.edit_column_title', 'Editar columna'),
                    input: 'text',
                    inputValue: currentTitle,
                    inputLabel: t('js.edit_column_label', 'Nuevo nombre de la columna'),
                    showCancelButton: true,
                    confirmButtonText: t('js.edit_column_save', 'Guardar columna'),
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    ...getSwalTheme(),
                    inputValidator: function (value) {
                        if (!value || !value.trim()) return t('js.field_required', 'El nombre es obligatorio');
                        return undefined;
                    },
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    columnUpdateForm.action = '/columns/' + columnId + '/update';
                    columnUpdateTitleInput.value = result.value.trim();
                    window.sessionStorage.setItem('prodify-toast', t('js.column_updated', 'Columna actualizada'));
                    columnUpdateForm.submit();
                });
            });
        }
    }

    /*
     * Botones para crear tareas dentro de cada columna.
     */
    const addCardButtons = document.querySelectorAll('.js-add-card');
    const cardForm = document.getElementById('cardCreateForm');
    const cardTitleInput = document.getElementById('cardTitleInput');

    if (addCardButtons.length && cardForm && cardTitleInput) {
        for (let c = 0; c < addCardButtons.length; c += 1) {
            addCardButtons[c].addEventListener('click', function () {
                if (!window.Swal) return;
                const columnId = this.getAttribute('data-column-id');
                if (!columnId) return;

                Swal.fire({
                    title: t('js.new_task_title', 'Nueva tarea'),
                    input: 'text',
                    inputLabel: t('js.task_name', 'Nombre de la tarea'),
                    inputPlaceholder: t('js.task_placeholder', 'Ej. Revisar copy'),
                    showCancelButton: true,
                    confirmButtonText: t('js.create', 'Crear'),
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    ...getSwalTheme(),
                    inputValidator: function (value) {
                        if (!value || !value.trim()) return t('js.field_required', 'El nombre es obligatorio');
                        return undefined;
                    },
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    cardForm.action = '/columns/' + columnId + '/cards/create';
                    cardTitleInput.value = result.value.trim();
                    cardForm.submit();
                });
            });
        }
    }

    /*
     * Antes de borrar, pido confirmacion al usuario.
     */
    const deleteColumnButtons = document.querySelectorAll('.js-delete-column');
    if (deleteColumnButtons.length) {
        for (let d = 0; d < deleteColumnButtons.length; d += 1) {
            deleteColumnButtons[d].addEventListener('click', function (event) {
                event.preventDefault();
                const form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: t('js.delete_column_title', 'Eliminar columna?'),
                    text: t('js.delete_column_text', 'Se borraran tambien todas las tareas.'),
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: t('js.confirm_delete', 'Si, eliminar'),
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    confirmButtonColor: '#c0264f',
                    ...getSwalTheme(),
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', t('js.column_deleted', 'Columna eliminada'));
                    form.submit();
                });
            });
        }
    }

    /*
     * Lo mismo para borrar tareas sueltas.
     */
    const deleteCardButtons = document.querySelectorAll('.js-delete-card');
    if (deleteCardButtons.length) {
        for (let dc = 0; dc < deleteCardButtons.length; dc += 1) {
            deleteCardButtons[dc].addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                const form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: t('js.delete_task_title', 'Eliminar tarea?'),
                    text: t('js.delete_task_text', 'Esta accion no se puede deshacer.'),
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: t('js.confirm_delete', 'Si, eliminar'),
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    confirmButtonColor: '#c0264f',
                    ...getSwalTheme(),
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', t('js.task_deleted', 'Tarea eliminada'));
                    form.submit();
                });
            });
        }
    }

    /*
     * ── Drag & drop de columnas ───────────────────────────────────────────────
     */
    (function () {
        var columnHandles = document.querySelectorAll('.js-column-drag-handle[data-column-id]');
        if (!columnHandles.length || !window.PRODIFY_BOARD_ID) return;

        var draggedColumn = null;
        var colPlaceholder = null;

        function getGrid() {
            var c = document.querySelector('.kanban-column[data-column-id]');
            return c ? c.parentElement : null;
        }

        function syncColumnOrder() {
            var cols = document.querySelectorAll('.kanban-column[data-column-id]');
            var ids = [];
            for (var i = 0; i < cols.length; i++) {
                var id = cols[i].getAttribute('data-column-id');
                if (id) ids.push(id);
            }
            if (!ids.length) return;
            fetch('/boards/' + window.PRODIFY_BOARD_ID + '/columns/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRF-Token': csrfToken },
                body: 'column_order=' + encodeURIComponent(ids.join(',')),
            }).catch(function () { window.location.reload(); });
        }

        function makePlaceholder(w, h) {
            var ph = document.createElement('div');
            ph.className = 'column-drag-placeholder';
            ph.style.cssText = 'width:' + w + 'px;min-width:' + w + 'px;height:' + h + 'px;' +
                'border:2px dashed rgba(99,102,241,.6);border-radius:12px;background:rgba(99,102,241,.06);flex-shrink:0;pointer-events:none;';
            return ph;
        }

        function removePlaceholder() {
            if (colPlaceholder && colPlaceholder.parentElement) colPlaceholder.parentElement.removeChild(colPlaceholder);
            colPlaceholder = null;
        }

        for (var hi = 0; hi < columnHandles.length; hi++) {
            columnHandles[hi].addEventListener('dragstart', function (e) {
                draggedColumn = this.closest('.kanban-column');
                if (!draggedColumn) return;
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', draggedColumn.getAttribute('data-column-id') || '');
                var rect = draggedColumn.getBoundingClientRect();
                var col = draggedColumn;
                setTimeout(function () {
                    col.classList.add('dragging-column');
                    colPlaceholder = makePlaceholder(rect.width, rect.height);
                    if (col.parentElement) col.parentElement.insertBefore(colPlaceholder, col);
                }, 0);
            });

            columnHandles[hi].addEventListener('dragend', function () {
                if (draggedColumn) draggedColumn.classList.remove('dragging-column');
                removePlaceholder();
                draggedColumn = null;
            });
        }

        var grid = getGrid();
        if (grid) {
            grid.addEventListener('dragover', function (e) {
                if (!draggedColumn) return;
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                var cols = Array.prototype.filter.call(
                    document.querySelectorAll('.kanban-column[data-column-id]'),
                    function (c) { return c !== draggedColumn; }
                );
                var insertBefore = null;
                for (var i = 0; i < cols.length; i++) {
                    var r = cols[i].getBoundingClientRect();
                    if (e.clientX < r.left + r.width / 2) { insertBefore = cols[i]; break; }
                }
                if (colPlaceholder) {
                    if (insertBefore) grid.insertBefore(colPlaceholder, insertBefore);
                    else grid.appendChild(colPlaceholder);
                }
            });

            grid.addEventListener('drop', function (e) {
                if (!draggedColumn) return;
                e.preventDefault();
                if (colPlaceholder && colPlaceholder.parentElement) {
                    colPlaceholder.parentElement.insertBefore(draggedColumn, colPlaceholder);
                    removePlaceholder();
                }
                draggedColumn.classList.remove('dragging-column');
                draggedColumn = null;
                syncColumnOrder();
            });
        }
    }());

    /*
     * ── Drag & drop de tarjetas ───────────────────────────────────────────────
     */
    (function () {
        var kanbanCards = document.querySelectorAll('.kanban-card[draggable="true"]');
        var kanbanColumns = document.querySelectorAll('.kanban-cards[data-column-id]');
        if (!kanbanCards.length || !kanbanColumns.length) return;

        var draggedCard = null;
        var sourceColumnId = null;
        var cardPlaceholder = null;

        function makeCardPlaceholder(h) {
            var ph = document.createElement('div');
            ph.className = 'kanban-card card-drag-placeholder';
            ph.style.cssText = 'height:' + h + 'px;border:2px dashed rgba(99,102,241,.6);' +
                'background:rgba(99,102,241,.06);border-radius:8px;pointer-events:none;flex-shrink:0;';
            return ph;
        }

        function removeCardPlaceholder() {
            if (cardPlaceholder && cardPlaceholder.parentElement) cardPlaceholder.parentElement.removeChild(cardPlaceholder);
            cardPlaceholder = null;
        }

        function getInsertionPoint(col, clientY) {
            var cards = Array.prototype.filter.call(
                col.querySelectorAll('.kanban-card[draggable="true"]'),
                function (c) { return c !== draggedCard; }
            );
            for (var i = 0; i < cards.length; i++) {
                var r = cards[i].getBoundingClientRect();
                if (clientY < r.top + r.height / 2) return cards[i];
            }
            return null;
        }

        for (var k = 0; k < kanbanCards.length; k++) {
            kanbanCards[k].addEventListener('dragstart', function (e) {
                draggedCard = this;
                var srcCol = this.closest('.kanban-cards');
                sourceColumnId = srcCol ? srcCol.getAttribute('data-column-id') : null;
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', this.getAttribute('data-card-id') || '');
                var rect = this.getBoundingClientRect();
                var card = this;
                setTimeout(function () {
                    card.classList.add('dragging');
                    cardPlaceholder = makeCardPlaceholder(rect.height);
                    if (card.parentElement) card.parentElement.insertBefore(cardPlaceholder, card.nextSibling);
                }, 0);
            });

            kanbanCards[k].addEventListener('dragend', function () {
                this.classList.remove('dragging');
                removeCardPlaceholder();
                draggedCard = null;
                for (var j = 0; j < kanbanColumns.length; j++) kanbanColumns[j].classList.remove('drag-over');
            });
        }

        for (var m = 0; m < kanbanColumns.length; m++) {
            kanbanColumns[m].addEventListener('dragover', function (e) {
                if (!draggedCard) return;
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
                if (!cardPlaceholder) return;
                var before = getInsertionPoint(this, e.clientY);
                var ghost = this.querySelector('.kanban-card.ghost:not(.card-drag-placeholder)');
                if (before) {
                    this.insertBefore(cardPlaceholder, before);
                } else {
                    this.insertBefore(cardPlaceholder, ghost || null);
                }
            });

            kanbanColumns[m].addEventListener('dragleave', function (e) {
                if (e.relatedTarget && this.contains(e.relatedTarget)) return;
                this.classList.remove('drag-over');
            });

            kanbanColumns[m].addEventListener('drop', function (e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                if (!draggedCard) return;
                var cardId = e.dataTransfer.getData('text/plain');
                if (!cardId) return;
                var targetColumnId = this.getAttribute('data-column-id');
                if (!targetColumnId) return;

                if (cardPlaceholder && cardPlaceholder.parentElement === this) {
                    this.insertBefore(draggedCard, cardPlaceholder);
                    removeCardPlaceholder();
                } else {
                    var ghost = this.querySelector('.kanban-card.ghost:not(.card-drag-placeholder)');
                    this.insertBefore(draggedCard, ghost || null);
                }
                draggedCard.classList.remove('dragging');

                if (sourceColumnId) {
                    var prevCol = document.querySelector('.kanban-cards[data-column-id="' + sourceColumnId + '"]');
                    if (prevCol && prevCol !== this && !prevCol.querySelector('.kanban-card[draggable="true"]')) {
                        var emptyCard = document.createElement('div');
                        emptyCard.className = 'kanban-card ghost';
                        emptyCard.textContent = t('js.empty_column', 'Sin tareas aun');
                        prevCol.appendChild(emptyCard);
                    }
                }
                var targetGhost = this.querySelector('.kanban-card.ghost:not(.card-drag-placeholder)');
                if (targetGhost && this.querySelector('.kanban-card[draggable="true"]')) targetGhost.remove();

                fetch('/cards/' + cardId + '/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRF-Token': csrfToken },
                    body: 'column_id=' + encodeURIComponent(targetColumnId),
                }).catch(function () { window.location.reload(); });
            });
        }
    }());

    /*
     * Confirmacion para borrar un tablero entero.
     */
    const deleteBoardButtons = document.querySelectorAll('.js-delete-board');
    if (deleteBoardButtons.length) {
        for (let b = 0; b < deleteBoardButtons.length; b += 1) {
            deleteBoardButtons[b].addEventListener('click', function (event) {
                event.preventDefault();
                const form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: t('js.delete_board_title', 'Borrar tablero?'),
                    text: t('js.delete_task_text', 'Esta accion no se puede deshacer.'),
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: t('js.confirm_delete_board', 'Si, borrar'),
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    confirmButtonColor: '#c0264f',
                    ...getSwalTheme(),
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', t('js.board_deleted', 'Tablero eliminado'));
                    form.submit();
                });
            });
        }
    }

    /*
     * Confirmacion para borrar un espacio con todo lo que tiene dentro.
     */
    const regLangDropdowns = document.querySelectorAll('.js-reg-lang-dropdown');
    for (let rli = 0; rli < regLangDropdowns.length; rli += 1) {
        (function (dropdown) {
            const trigger = dropdown.querySelector('.js-reg-lang-trigger');
            const menu = dropdown.querySelector('.topbar-language-menu');
            const hiddenInput = dropdown.querySelector('input[name="preferred_language"]');
            const flagEl = dropdown.querySelector('.js-reg-lang-flag');
            const labelEl = dropdown.querySelector('.js-reg-lang-label');
            const options = dropdown.querySelectorAll('.js-reg-lang-option');
            if (!trigger || !menu || !hiddenInput) return;

            trigger.addEventListener('click', function () {
                const isOpen = !menu.hasAttribute('hidden');
                if (isOpen) {
                    menu.setAttribute('hidden', 'hidden');
                    trigger.setAttribute('aria-expanded', 'false');
                } else {
                    menu.removeAttribute('hidden');
                    trigger.setAttribute('aria-expanded', 'true');
                }
            });

            for (let oi = 0; oi < options.length; oi += 1) {
                options[oi].addEventListener('click', function () {
                    const value = this.getAttribute('data-language-value') || '';
                    if (!value) return;
                    hiddenInput.value = value;
                    const optFlag = this.querySelector('.topbar-language-option-flag');
                    const optLabel = this.querySelector('.topbar-language-option-label');
                    if (flagEl && optFlag) flagEl.innerHTML = optFlag.innerHTML;
                    if (labelEl && optLabel) labelEl.textContent = optLabel.textContent;
                    for (let k = 0; k < options.length; k += 1) {
                        options[k].setAttribute('aria-pressed', options[k] === this ? 'true' : 'false');
                    }
                    menu.setAttribute('hidden', 'hidden');
                    trigger.setAttribute('aria-expanded', 'false');
                });
            }

            document.addEventListener('click', function (evt) {
                if (!dropdown.contains(evt.target)) {
                    menu.setAttribute('hidden', 'hidden');
                    trigger.setAttribute('aria-expanded', 'false');
                }
            });
        }(regLangDropdowns[rli]));
    }

    const deleteWorkspaceButtons = document.querySelectorAll('.js-delete-workspace');
    if (deleteWorkspaceButtons.length) {
        for (let w = 0; w < deleteWorkspaceButtons.length; w += 1) {
            deleteWorkspaceButtons[w].addEventListener('click', function (event) {
                event.preventDefault();
                const form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: t('js.delete_workspace_title', 'Borrar espacio de trabajo?'),
                    text: t('js.delete_workspace_text', 'Se borraran tambien todos sus tableros.'),
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: t('js.confirm_delete_workspace', 'Si, borrar espacio'),
                    cancelButtonText: t('js.cancel', 'Cancelar'),
                    confirmButtonColor: '#c0264f',
                    ...getSwalTheme(),
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', t('js.workspace_deleted', 'Espacio eliminado'));
                    form.submit();
                });
            });
        }
    }
});
