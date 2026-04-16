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
        it: { dark: 'Attiva la modalita scura', light: 'Attiva la modalita chiara' },
        pt: { dark: 'Ativar modo escuro', light: 'Ativar modo claro' },
        ar: { dark: 'تفعيل الوضع الداكن', light: 'تفعيل الوضع الفاتح' },
        hi: { dark: 'डार्क मोड चालू करें', light: 'लाइट मोड चालू करें' },
        'zh-CN': { dark: '切换到深色模式', light: '切换到浅色模式' },
        ja: { dark: 'ダークモードに切り替える', light: 'ライトモードに切り替える' }
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
        const options = ['<option value="">Selecciona un espacio</option>'];
        for (let i = 0; i < creationWorkspaces.length; i += 1) {
            const workspace = creationWorkspaces[i];
            const selected = String(selectedWorkspaceId || '') === String(workspace.id) ? ' selected' : '';
            options.push('<option value="' + escapeHtml(workspace.id) + '"' + selected + '>' + escapeHtml(workspace.name) + '</option>');
        }
        options.push('<option value="__new__">Crear espacio nuevo</option>');
        return options.join('');
    }

    function buildTemplatePicker(selectedTemplateId) {
        if (!creationTemplates.length) {
            return '<div class="board-creator-empty">No hay plantillas disponibles todavía.</div>';
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
        const columns = template && template.columns ? template.columns.slice(0, 3) : ['Pendiente', 'En curso', 'Listo'];
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
                : 'Crea un tablero vacio con la estructura base y personalizalo despues.';
        }
        if (pickerWrap) {
            pickerWrap.hidden = mode !== 'template';
        }
        if (appearanceWrap) {
            appearanceWrap.hidden = mode !== 'normal';
        }
        if (confirmButton) {
            confirmButton.textContent = mode === 'template' ? 'Crear tablero con plantilla' : 'Crear tablero';
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
            title: initialMode === 'template' ? 'Crear tablero con plantilla' : 'Crear tablero',
            width: 620,
            showCancelButton: true,
            cancelButtonText: 'Cancelar',
            confirmButtonText: initialMode === 'template' ? 'Crear tablero con plantilla' : 'Crear tablero',
            confirmButtonColor: '#2f63ff',
            background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
            color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
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
                            '<button type="button" class="board-mode-btn' + (initialMode === 'normal' ? ' is-active' : '') + '" data-mode="normal">Crear normal</button>' +
                            '<button type="button" class="board-mode-btn' + (initialMode === 'template' ? ' is-active' : '') + '" data-mode="template">Usar plantilla</button>' +
                        '</div>'
                    ) +
                    '<div class="board-creator-preview-shell">' +
                        '<div class="board-creator-preview-top"><span>Vista previa</span><span class="board-creator-preview-icon"></span></div>' +
                        '<div class="board-creator-preview" data-board-preview></div>' +
                    '</div>' +
                    '<div class="board-creator-template-copy" data-template-summary></div>' +
                    '<div class="board-creator-appearance" data-appearance-wrap' + (initialMode === 'normal' ? '' : ' hidden') + '>' +
                        '<div class="board-creator-field board-creator-field-tight"><label>Fondo del tablero</label></div>' +
                        '<div class="board-color-grid">' +
                            '<button type="button" class="board-color-option is-active" data-color-value="#1d4ed8" style="background:#1d4ed8"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#0f766e" style="background:#0f766e"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#be185d" style="background:#be185d"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#7c3aed" style="background:#7c3aed"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#ea580c" style="background:#ea580c"></button>' +
                            '<button type="button" class="board-color-option" data-color-value="#334155" style="background:#334155"></button>' +
                        '</div>' +
                        '<div class="board-cover-upload">' +
                            '<label for="swal-board-cover" class="board-cover-upload-btn">Subir imagen</label>' +
                            '<input id="swal-board-cover" type="file" accept=".jpg,.jpeg,.png,.svg,.webp,image/jpeg,image/png,image/svg+xml,image/webp">' +
                            '<span class="board-cover-upload-name" id="swal-board-cover-name">Ningún archivo seleccionado</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="board-creator-field">' +
                        '<label for="swal-board-title">Titulo del tablero</label>' +
                        '<input id="swal-board-title" class="swal2-input board-creator-input" value="' + escapeHtml(initialBoardName) + '" placeholder="Ej. Sprint de abril">' +
                    '</div>' +
                    '<div class="board-creator-field">' +
                        '<label for="swal-board-workspace">Espacio de trabajo</label>' +
                        '<select id="swal-board-workspace" class="swal2-select board-creator-select">' + buildWorkspaceOptions(initialWorkspaceId) + '</select>' +
                    '</div>' +
                    '<div class="board-creator-field" data-new-workspace-field hidden>' +
                        '<label for="swal-new-workspace">Nombre del nuevo espacio</label>' +
                        '<input id="swal-new-workspace" class="swal2-input board-creator-input" value="' + escapeHtml(initialWorkspaceName) + '" placeholder="Ej. Producto Q2">' +
                    '</div>' +
                    '<div class="board-creator-template-wrap" data-template-wrap' + (initialMode === 'template' ? '' : ' hidden') + '>' +
                        '<div class="board-creator-field board-creator-field-tight"><label>Plantilla</label></div>' +
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
                            coverName.textContent = this.files && this.files[0] ? this.files[0].name : 'Ningún archivo seleccionado';
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
                    Swal.showValidationMessage('Es necesario indicar el titulo del tablero');
                    return false;
                }
                if (!workspaceValue) {
                    Swal.showValidationMessage('Selecciona un espacio de trabajo o crea uno nuevo');
                    return false;
                }
                if (workspaceValue === '__new__' && !newWorkspaceName) {
                    Swal.showValidationMessage('Escribe el nombre del nuevo espacio');
                    return false;
                }
                if (mode === 'template' && !templateId) {
                    Swal.showValidationMessage('Selecciona una plantilla para continuar');
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
                window.sessionStorage.setItem('prodify-toast', 'Tablero creado desde plantilla');
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
            let successToast = 'Tablero creado correctamente';
            if (value.workspaceValue === '__new__') {
                formData.append('workspace_name', value.newWorkspaceName);
                endpoint = '/workspaces/create';
                successToast = 'Espacio y tablero creados correctamente';
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
                if (!response.ok) throw new Error('No se pudo crear el tablero');
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
                    title: 'No se pudo crear el tablero',
                    text: 'Revisa la imagen elegida o vuelve a intentarlo.',
                    confirmButtonColor: '#2f63ff',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
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
                    title: 'Configuracion del espacio',
                    input: 'text',
                    inputLabel: 'Nombre del espacio',
                    inputValue: workspaceName,
                    inputPlaceholder: 'Ej. Producto y roadmap',
                    confirmButtonText: 'Guardar cambios',
                    showCancelButton: true,
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#2f63ff',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                    inputValidator: function (value) {
                        if (!value || !value.trim()) return 'El nombre es obligatorio';
                        return undefined;
                    },
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    workspaceUpdateForm.action = '/workspaces/' + workspaceId + '/update';
                    workspaceUpdateNameInput.value = result.value.trim();
                    window.sessionStorage.setItem('prodify-toast', 'Espacio actualizado correctamente');
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
                title: 'Actualizar email',
                input: 'email',
                inputLabel: 'Nuevo correo electronico',
                inputValue: currentEmail,
                inputPlaceholder: 'correo@ejemplo.com',
                confirmButtonText: 'Guardar email',
                showCancelButton: true,
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#2f63ff',
                background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                inputValidator: function (value) {
                    if (!value || !value.trim()) return 'Introduce un correo electronico';
                    const emailValue = value.trim();
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailPattern.test(emailValue)) return 'Introduce un correo electronico valido';
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
                title: 'Nueva columna',
                input: 'text',
                inputLabel: 'Nombre de la columna',
                inputPlaceholder: 'Ej. En revision',
                showCancelButton: true,
                confirmButtonText: 'Crear',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#2f63ff',
                background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                inputValidator: function (value) {
                    if (!value || !value.trim()) return 'El nombre es obligatorio';
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
                    title: 'Editar columna',
                    input: 'text',
                    inputValue: currentTitle,
                    inputLabel: 'Nuevo nombre de la columna',
                    showCancelButton: true,
                    confirmButtonText: 'Guardar columna',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#2f63ff',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                    inputValidator: function (value) {
                        if (!value || !value.trim()) return 'El nombre es obligatorio';
                        return undefined;
                    },
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    columnUpdateForm.action = '/columns/' + columnId + '/update';
                    columnUpdateTitleInput.value = result.value.trim();
                    window.sessionStorage.setItem('prodify-toast', 'Columna actualizada');
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
                    title: 'Nueva tarea',
                    input: 'text',
                    inputLabel: 'Nombre de la tarea',
                    inputPlaceholder: 'Ej. Revisar copy',
                    showCancelButton: true,
                    confirmButtonText: 'Crear',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#2f63ff',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                    inputValidator: function (value) {
                        if (!value || !value.trim()) return 'El nombre es obligatorio';
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
                    title: 'Eliminar columna?',
                    text: 'Se borraran tambien todas las tareas.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, eliminar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Columna eliminada');
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
                    title: 'Eliminar tarea?',
                    text: 'Esta accion no se puede deshacer.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, eliminar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Tarea eliminada');
                    form.submit();
                });
            });
        }
    }

    /*
     * Elementos necesarios para el drag and drop del kanban.
     */
    const kanbanColumnShells = document.querySelectorAll('.kanban-column[data-column-id]');
    const columnDragHandles = document.querySelectorAll('.js-column-drag-handle[data-column-id]');
    const kanbanCards = document.querySelectorAll('.kanban-card[draggable="true"]');
    const kanbanColumns = document.querySelectorAll('.kanban-cards[data-column-id]');

    if (kanbanColumnShells.length && columnDragHandles.length && window.PRODIFY_BOARD_ID) {
        let draggedColumn = null;

        const syncColumnOrder = function () {
            const orderedIds = [];
            const orderedColumns = document.querySelectorAll('.kanban-column[data-column-id]');
            for (let index = 0; index < orderedColumns.length; index += 1) {
                const columnId = orderedColumns[index].getAttribute('data-column-id');
                if (columnId) orderedIds.push(columnId);
            }
            if (!orderedIds.length) return;

            fetch('/boards/' + window.PRODIFY_BOARD_ID + '/columns/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRF-Token': csrfToken,
                },
                body: 'column_order=' + encodeURIComponent(orderedIds.join(',')),
            }).catch(function () {
                window.location.reload();
            });
        };

        for (let handleIndex = 0; handleIndex < columnDragHandles.length; handleIndex += 1) {
            columnDragHandles[handleIndex].addEventListener('dragstart', function (event) {
                draggedColumn = this.closest('.kanban-column');
                if (!draggedColumn) return;
                draggedColumn.classList.add('dragging-column');
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', draggedColumn.getAttribute('data-column-id') || '');
            });

            columnDragHandles[handleIndex].addEventListener('dragend', function () {
                if (draggedColumn) {
                    draggedColumn.classList.remove('dragging-column');
                }
                for (let columnIndex = 0; columnIndex < kanbanColumnShells.length; columnIndex += 1) {
                    kanbanColumnShells[columnIndex].classList.remove('drag-over-column');
                }
                draggedColumn = null;
            });
        }

        for (let shellIndex = 0; shellIndex < kanbanColumnShells.length; shellIndex += 1) {
            kanbanColumnShells[shellIndex].addEventListener('dragover', function (event) {
                if (!draggedColumn || draggedColumn === this) return;
                event.preventDefault();
                this.classList.add('drag-over-column');
            });

            kanbanColumnShells[shellIndex].addEventListener('dragleave', function () {
                this.classList.remove('drag-over-column');
            });

            kanbanColumnShells[shellIndex].addEventListener('drop', function (event) {
                if (!draggedColumn || draggedColumn === this) return;
                event.preventDefault();

                const kanbanGrid = this.parentElement;
                if (!kanbanGrid) return;

                this.classList.remove('drag-over-column');
                const bounds = this.getBoundingClientRect();
                const insertAfter = event.clientX > bounds.left + (bounds.width / 2);
                kanbanGrid.insertBefore(draggedColumn, insertAfter ? this.nextSibling : this);
                syncColumnOrder();
            });
        }
    }

    if (kanbanCards.length && kanbanColumns.length) {
        /*
         * Guardo la columna origen para comparar luego con la de destino.
         */
        let sourceColumnId = null;

        for (let k = 0; k < kanbanCards.length; k += 1) {
            kanbanCards[k].addEventListener('dragstart', function (event) {
                this.classList.add('dragging');
                const sourceColumn = this.closest('.kanban-cards');
                sourceColumnId = sourceColumn ? sourceColumn.getAttribute('data-column-id') : null;
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', this.getAttribute('data-card-id'));
            });

            kanbanCards[k].addEventListener('dragend', function () {
                this.classList.remove('dragging');
                for (let j = 0; j < kanbanColumns.length; j += 1) {
                    kanbanColumns[j].classList.remove('drag-over');
                }
            });
        }

        /*
         * Aqui controlo el movimiento entre columnas.
         */
        for (let m = 0; m < kanbanColumns.length; m += 1) {
            kanbanColumns[m].addEventListener('dragover', function (event) {
                event.preventDefault();
                this.classList.add('drag-over');
            });

            kanbanColumns[m].addEventListener('dragleave', function () {
                this.classList.remove('drag-over');
            });

            kanbanColumns[m].addEventListener('drop', function (event) {
                event.preventDefault();
                this.classList.remove('drag-over');

                const cardId = event.dataTransfer.getData('text/plain');
                if (!cardId) return;
                const targetColumnId = this.getAttribute('data-column-id');
                if (!targetColumnId) return;

                /*
                 * Primero muevo la tarjeta en la interfaz.
                 */
                const card = document.querySelector('.kanban-card[data-card-id="' + cardId + '"]');
                if (card) {
                    const ghostCard = this.querySelector('.kanban-card.ghost');
                    if (ghostCard) ghostCard.remove();
                    this.appendChild(card);
                }

                if (sourceColumnId && sourceColumnId !== targetColumnId) {
                    const previousColumn = document.querySelector('.kanban-cards[data-column-id="' + sourceColumnId + '"]');
                    if (previousColumn && !previousColumn.querySelector('.kanban-card[draggable="true"]')) {
                        /*
                         * If the column becomes empty, show the placeholder again.
                         */
                        const emptyCard = document.createElement('div');
                        emptyCard.className = 'kanban-card ghost';
                        emptyCard.textContent = 'Sin tareas aun';
                        previousColumn.appendChild(emptyCard);
                    }
                }

                fetch('/cards/' + cardId + '/move', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRF-Token': csrfToken,
                    },
                    body: 'column_id=' + encodeURIComponent(targetColumnId),
                }).catch(function () {
                    /*
                     * Si falla la peticion, recargo la pagina para evitar desajustes.
                     */
                    window.location.reload();
                });
            });
        }
    }

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
                    title: 'Borrar tablero?',
                    text: 'Esta accion no se puede deshacer.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, borrar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Tablero eliminado');
                    form.submit();
                });
            });
        }
    }

    /*
     * Confirmacion para borrar un espacio con todo lo que tiene dentro.
     */
    const deleteWorkspaceButtons = document.querySelectorAll('.js-delete-workspace');
    if (deleteWorkspaceButtons.length) {
        for (let w = 0; w < deleteWorkspaceButtons.length; w += 1) {
            deleteWorkspaceButtons[w].addEventListener('click', function (event) {
                event.preventDefault();
                const form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: 'Borrar espacio de trabajo?',
                    text: 'Se borraran tambien todos sus tableros.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, borrar espacio',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Espacio eliminado');
                    form.submit();
                });
            });
        }
    }
});
