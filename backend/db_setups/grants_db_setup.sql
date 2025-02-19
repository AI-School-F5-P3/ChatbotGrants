-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS grants_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE grants_db;

-- Tabla principal de convocatorias
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

-- Tabla de detalles de convocatorias
CREATE TABLE IF NOT EXISTS fund_details (
    id BIGINT PRIMARY KEY,
    fund_id BIGINT NOT NULL,
    sede_electronica VARCHAR(255),
    codigo_bdns VARCHAR(50),
    tipo_convocatoria VARCHAR(100),
    presupuesto_total DECIMAL(15,2),
    descripcion_finalidad VARCHAR(200),
    descripcion_bases_reguladoras TEXT,
    url_bases_reguladoras VARCHAR(255),
    se_publica_diario_oficial BOOLEAN DEFAULT TRUE,
    abierto BOOLEAN DEFAULT TRUE,
    fecha_inicio_solicitud DATE,
    fecha_fin_solicitud DATE,
    text_inicio TEXT,
    text_fin TEXT,
    ayuda_estado VARCHAR(50),
    url_ayuda_estado VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES funds(id)
);

-- Índices para optimizar búsquedas
CREATE INDEX idx_funds_fecha_recepcion ON funds(fecha_recepcion);
CREATE INDEX idx_fund_details_fecha_fin ON fund_details(fecha_fin_solicitud);
CREATE INDEX idx_fund_details_abierto ON fund_details(abierto);
CREATE INDEX idx_fund_details_presupuesto ON fund_details(presupuesto_total);