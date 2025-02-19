-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS grants_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE grants_db;

-- Probemos crear las tablas en orden específico para identificar cualquier problema

-- 1. Tabla para sectores económicos
CREATE TABLE IF NOT EXISTS sectores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_sector (codigo)
);

-- 2. Tabla principal de convocatorias
CREATE TABLE IF NOT EXISTS funds (
    id BIGINT PRIMARY KEY,
    numero_convocatoria VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    descripcion_leng TEXT,
    fecha_recepcion DATE NOT NULL,
    nivel1 VARCHAR(100),
    nivel2 VARCHAR(200),
    nivel3 VARCHAR(200),
    mrr BOOLEAN DEFAULT FALSE,
    codigo_invente VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_convocatoria (numero_convocatoria)
);

-- 3. Tabla de relación entre convocatorias y sectores
CREATE TABLE IF NOT EXISTS funds_sectores (
    fund_id BIGINT,
    sector_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fund_id, sector_id),
    FOREIGN KEY (fund_id) REFERENCES funds(id),
    FOREIGN KEY (sector_id) REFERENCES sectores(id)
);

-- Verificación
-- Después de crear estas tablas, podemos verificar su estructura con:
-- SHOW CREATE TABLE funds;
-- SHOW CREATE TABLE sectores;
-- SHOW CREATE TABLE funds_sectores;