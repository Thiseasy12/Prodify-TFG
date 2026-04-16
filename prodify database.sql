CREATE DATABASE IF NOT EXISTS prodify_db;
USE prodify_db;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS board_columns;
DROP TABLE IF EXISTS boards;
DROP TABLE IF EXISTS workspace_members;
DROP TABLE IF EXISTS workspaces;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- Tabla de Usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Perfil de usuario
CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    display_name VARCHAR(80) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Espacios de trabajo
CREATE TABLE workspaces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_workspaces_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Miembros de los espacios
CREATE TABLE workspace_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workspace_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'lector',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_workspace_member_user (workspace_id, user_id),
    INDEX idx_workspace_members_workspace (workspace_id),
    INDEX idx_workspace_members_user (user_id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tableros
CREATE TABLE boards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workspace_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_boards_workspace (workspace_id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Columnas del tablero
CREATE TABLE board_columns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    board_id INT NOT NULL,
    title VARCHAR(120) NOT NULL,
    position INT NOT NULL,
    INDEX idx_columns_board (board_id),
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
);

-- Tarjetas
CREATE TABLE cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    column_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cards_column (column_id),
    FOREIGN KEY (column_id) REFERENCES board_columns(id) ON DELETE CASCADE
);
