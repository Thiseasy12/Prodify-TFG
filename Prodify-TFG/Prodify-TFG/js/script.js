document.addEventListener('DOMContentLoaded', function () {
    var root = document.body;
    var themeToggle = document.getElementById('themeToggle');
    var savedTheme = window.localStorage.getItem('prodify-theme');

    if (savedTheme === 'light') {
        root.classList.add('theme-light');
    }

    function syncThemeText() {
        if (!themeToggle) return;
        if (root.classList.contains('theme-light')) {
            themeToggle.textContent = '☀';
            themeToggle.setAttribute('aria-label', 'Activar modo oscuro');
        } else {
            themeToggle.textContent = '🌙';
            themeToggle.setAttribute('aria-label', 'Activar modo claro');
        }
    }

    if (themeToggle) {
        syncThemeText();
        themeToggle.addEventListener('click', function () {
            root.classList.toggle('theme-light');
            if (root.classList.contains('theme-light')) {
                window.localStorage.setItem('prodify-theme', 'light');
            } else {
                window.localStorage.setItem('prodify-theme', 'dark');
            }
            syncThemeText();
        });
    }

    var pendingToast = window.sessionStorage.getItem('prodify-toast');
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

    var accountToggle = document.getElementById('accountToggle');
    var accountMenu = document.getElementById('accountMenu');
    if (accountToggle && accountMenu) {
        accountToggle.addEventListener('click', function () {
            if (accountMenu.hasAttribute('hidden')) {
                accountMenu.removeAttribute('hidden');
            } else {
                accountMenu.setAttribute('hidden', 'hidden');
            }
        });

        document.addEventListener('click', function (event) {
            if (!accountMenu.contains(event.target) && event.target !== accountToggle) {
                accountMenu.setAttribute('hidden', 'hidden');
            }
        });
    }

    var workspaceCreateButton = document.querySelector('.js-create-workspace');
    var workspaceForm = document.getElementById('workspaceCreateForm');
    var workspaceNameInput = document.getElementById('workspaceNameInput');

    if (workspaceCreateButton && workspaceForm && workspaceNameInput) {
        workspaceCreateButton.addEventListener('click', function () {
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
                background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
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

    var boardForm = document.getElementById('boardCreateForm');
    var boardNameInput = document.getElementById('boardNameInput');
    var boardCreateCards = document.querySelectorAll('.js-create-board');

    if (boardForm && boardNameInput && boardCreateCards.length) {
        for (var i = 0; i < boardCreateCards.length; i += 1) {
            boardCreateCards[i].addEventListener('click', function () {
                if (!window.Swal) return;
                var workspaceId = this.getAttribute('data-workspace-id');
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
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
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

    var templateButtons = document.querySelectorAll('.js-use-template');
    var templateForm = document.getElementById('templateCreateForm');
    var templateWorkspaceInput = document.getElementById('templateWorkspaceInput');
    var templateBoardInput = document.getElementById('templateBoardInput');
    var templateIdInput = document.getElementById('templateIdInput');

    if (templateButtons.length && templateForm && templateWorkspaceInput && templateBoardInput && templateIdInput) {
        for (var t = 0; t < templateButtons.length; t += 1) {
            templateButtons[t].addEventListener('click', function () {
                if (!window.Swal) return;

                var templateName = this.getAttribute('data-template-name') || 'Nuevo tablero';
                var templateId = this.getAttribute('data-template-id') || '';

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
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                    preConfirm: function () {
                        var workspaceName = document.getElementById('swal-workspace').value.trim();
                        var boardName = document.getElementById('swal-board').value.trim();
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

    var addColumnButton = document.querySelector('.js-add-column');
    var columnForm = document.getElementById('columnCreateForm');
    var columnTitleInput = document.getElementById('columnTitleInput');

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
                background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
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

    var addCardButtons = document.querySelectorAll('.js-add-card');
    var cardForm = document.getElementById('cardCreateForm');
    var cardTitleInput = document.getElementById('cardTitleInput');

    if (addCardButtons.length && cardForm && cardTitleInput) {
        for (var c = 0; c < addCardButtons.length; c += 1) {
            addCardButtons[c].addEventListener('click', function () {
                if (!window.Swal) return;
                var columnId = this.getAttribute('data-column-id');
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
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
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

    var deleteColumnButtons = document.querySelectorAll('.js-delete-column');
    if (deleteColumnButtons.length) {
        for (var d = 0; d < deleteColumnButtons.length; d += 1) {
            deleteColumnButtons[d].addEventListener('click', function (event) {
                event.preventDefault();
                var form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: 'Eliminar columna?',
                    text: 'Se borraran tambien todas las tareas.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, eliminar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Columna eliminada');
                    form.submit();
                });
            });
        }
    }

    var deleteCardButtons = document.querySelectorAll('.js-delete-card');
    if (deleteCardButtons.length) {
        for (var dc = 0; dc < deleteCardButtons.length; dc += 1) {
            deleteCardButtons[dc].addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                var form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: 'Eliminar tarea?',
                    text: 'Esta accion no se puede deshacer.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, eliminar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Tarea eliminada');
                    form.submit();
                });
            });
        }
    }

    var kanbanCards = document.querySelectorAll('.kanban-card[draggable="true"]');
    var kanbanColumns = document.querySelectorAll('.kanban-cards[data-column-id]');

    if (kanbanCards.length && kanbanColumns.length) {
        var sourceColumnId = null;

        for (var k = 0; k < kanbanCards.length; k += 1) {
            kanbanCards[k].addEventListener('dragstart', function (event) {
                this.classList.add('dragging');
                var parentColumn = this.closest('.kanban-cards');
                sourceColumnId = parentColumn ? parentColumn.getAttribute('data-column-id') : null;
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', this.getAttribute('data-card-id'));
            });

            kanbanCards[k].addEventListener('dragend', function () {
                this.classList.remove('dragging');
                for (var j = 0; j < kanbanColumns.length; j += 1) {
                    kanbanColumns[j].classList.remove('drag-over');
                }
            });
        }

        for (var m = 0; m < kanbanColumns.length; m += 1) {
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

                var cardId = event.dataTransfer.getData('text/plain');
                if (!cardId) return;
                var targetColumnId = this.getAttribute('data-column-id');
                if (!targetColumnId) return;

                var cardEl = document.querySelector('.kanban-card[data-card-id="' + cardId + '"]');
                if (cardEl) {
                    var ghostCard = this.querySelector('.kanban-card.ghost');
                    if (ghostCard) ghostCard.remove();
                    this.appendChild(cardEl);
                }

                if (sourceColumnId && sourceColumnId !== targetColumnId) {
                    var sourceColumn = document.querySelector('.kanban-cards[data-column-id="' + sourceColumnId + '"]');
                    if (sourceColumn && !sourceColumn.querySelector('.kanban-card[draggable="true"]')) {
                        var empty = document.createElement('div');
                        empty.className = 'kanban-card ghost';
                        empty.textContent = 'Sin tareas aun';
                        sourceColumn.appendChild(empty);
                    }
                }

                fetch('/cards/' + cardId + '/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'column_id=' + encodeURIComponent(targetColumnId),
                }).catch(function () {
                    window.location.reload();
                });
            });
        }
    }

    var deleteBoards = document.querySelectorAll('.js-delete-board');
    if (deleteBoards.length) {
        for (var b = 0; b < deleteBoards.length; b += 1) {
            deleteBoards[b].addEventListener('click', function (event) {
                event.preventDefault();
                var form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: 'Borrar tablero?',
                    text: 'Esta accion no se puede deshacer.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, borrar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Tablero eliminado');
                    form.submit();
                });
            });
        }
    }

    var deleteWorkspaceButtons = document.querySelectorAll('.js-delete-workspace');
    if (deleteWorkspaceButtons.length) {
        for (var w = 0; w < deleteWorkspaceButtons.length; w += 1) {
            deleteWorkspaceButtons[w].addEventListener('click', function (event) {
                event.preventDefault();
                var form = this.closest('form');
                if (!form || !window.Swal) return;

                Swal.fire({
                    title: 'Borrar espacio de trabajo?',
                    text: 'Se borraran tambien todos sus tableros.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Si, borrar espacio',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#c0264f',
                    background: root.classList.contains('theme-light') ? '#f4f8ff' : '#0c1629',
                    color: root.classList.contains('theme-light') ? '#14305f' : '#e6eeff',
                }).then(function (result) {
                    if (!result.isConfirmed) return;
                    window.sessionStorage.setItem('prodify-toast', 'Espacio eliminado');
                    form.submit();
                });
            });
        }
    }
});
