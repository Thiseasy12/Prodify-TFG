document.addEventListener('DOMContentLoaded', function () {
    /*
     * Cojo los elementos principales cuando ya se ha cargado el DOM.
     */
    const body = document.body;
    const themeButton = document.getElementById('themeToggle');
    const savedTheme = window.localStorage.getItem('prodify-theme');

    /*
     * Si el usuario habia guardado el tema claro, lo aplico al entrar.
     */
    if (savedTheme === 'light') {
        body.classList.add('theme-light');
    }

    /*
     * Cambio el icono del boton segun el tema activo.
     */
    function updateThemeText() {
        if (!themeButton) return;
        if (body.classList.contains('theme-light')) {
            themeButton.textContent = '☀';
            themeButton.setAttribute('aria-label', 'Activar modo oscuro');
        } else {
            themeButton.textContent = '🌙';
            themeButton.setAttribute('aria-label', 'Activar modo claro');
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
            if (!accountMenu.contains(event.target) && event.target !== accountButton) {
                accountMenu.setAttribute('hidden', 'hidden');
            }
        });
    }

    /*
     * Boton y formulario para crear espacios de trabajo.
     */
    const createWorkspaceButton = document.querySelector('.js-create-workspace');
    const workspaceForm = document.getElementById('workspaceCreateForm');
    const workspaceNameInput = document.getElementById('workspaceNameInput');

    if (createWorkspaceButton && workspaceForm && workspaceNameInput) {
        createWorkspaceButton.addEventListener('click', function () {
            if (!window.Swal) return;
            Swal.fire({
                title: 'Nuevo espacio de trabajo',
                input: 'text',
                inputLabel: 'Escribe el nombre',
                inputPlaceholder: 'Ej. Marketing y Ventas',
                confirmButtonText: 'Crear espacio',
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
                workspaceNameInput.value = result.value.trim();
                window.sessionStorage.setItem('prodify-toast', 'Espacio creado correctamente');
                workspaceForm.submit();
            });
        });
    }

    const boardForm = document.getElementById('boardCreateForm');
    const boardNameInput = document.getElementById('boardNameInput');
    const createBoardCards = document.querySelectorAll('.js-create-board');

    if (boardForm && boardNameInput && createBoardCards.length) {
        /*
         * Recorro todas las tarjetas que permiten crear un tablero.
         */
        for (let i = 0; i < createBoardCards.length; i += 1) {
            createBoardCards[i].addEventListener('click', function () {
                if (!window.Swal) return;
                const workspaceId = this.getAttribute('data-workspace-id');
                if (!workspaceId) return;

                Swal.fire({
                    title: 'Nuevo tablero',
                    input: 'text',
                    inputLabel: 'Nombre del tablero',
                    inputPlaceholder: 'Ej. Plan semanal',
                    confirmButtonText: 'Crear tablero',
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
                    boardForm.action = '/workspaces/' + workspaceId + '/boards/create';
                    boardNameInput.value = result.value.trim();
                    window.sessionStorage.setItem('prodify-toast', 'Tablero creado correctamente');
                    boardForm.submit();
                });
            });
        }
    }

    const templateButtons = document.querySelectorAll('.js-use-template');
    const templateForm = document.getElementById('templateCreateForm');
    const templateWorkspaceInput = document.getElementById('templateWorkspaceInput');
    const templateBoardInput = document.getElementById('templateBoardInput');
    const templateIdInput = document.getElementById('templateIdInput');

    if (templateButtons.length && templateForm && templateWorkspaceInput && templateBoardInput && templateIdInput) {
        /*
         * Esto sirve para crear un tablero a partir de una plantilla.
         */
        for (let t = 0; t < templateButtons.length; t += 1) {
            templateButtons[t].addEventListener('click', function () {
                if (!window.Swal) return;

                const templateName = this.getAttribute('data-template-name') || 'Nuevo tablero';
                const templateId = this.getAttribute('data-template-id') || '';

                Swal.fire({
                    title: 'Usar plantilla',
                    html:
                        '<label class="swal-label">Nombre del espacio de trabajo</label>' +
                        '<input id="swal-workspace" class="swal2-input" placeholder="Ej. Equipo Creativo">' +
                        '<label class="swal-label">Nombre del tablero</label>' +
                        '<input id="swal-board" class="swal2-input" value="' + templateName + '">',
                    focusConfirm: false,
                    showCancelButton: true,
                    confirmButtonText: 'Crear espacio y tablero',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#2f63ff',
                    background: body.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: body.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                    preConfirm: function () {
                        const workspaceName = document.getElementById('swal-workspace').value.trim();
                        const boardName = document.getElementById('swal-board').value.trim();
                        if (!workspaceName) {
                            Swal.showValidationMessage('El espacio de trabajo es obligatorio');
                            return false;
                        }
                        if (!boardName) {
                            Swal.showValidationMessage('El nombre del tablero es obligatorio');
                            return false;
                        }
                        return { workspaceName: workspaceName, boardName: boardName };
                    },
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    templateWorkspaceInput.value = result.value.workspaceName;
                    templateBoardInput.value = result.value.boardName;
                    templateIdInput.value = templateId;
                    window.sessionStorage.setItem('prodify-toast', 'Tablero creado desde plantilla');
                    templateForm.submit();
                });
            });
        }
    }

    /*
     * Formulario para crear columnas.
     */
    const addColumnButton = document.querySelector('.js-add-column');
    const columnForm = document.getElementById('columnCreateForm');
    const columnTitleInput = document.getElementById('columnTitleInput');

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
    const kanbanCards = document.querySelectorAll('.kanban-card[draggable="true"]');
    const kanbanColumns = document.querySelectorAll('.kanban-cards[data-column-id]');

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
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
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
