USE grants_db;

-- Tabla para tipos de beneficiarios
CREATE TABLE IF NOT EXISTS tipos_beneficiarios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10),
    descripcion VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_beneficiario (descripcion)
);

-- Tabla de relación entre convocatorias y beneficiarios
CREATE TABLE IF NOT EXISTS funds_beneficiarios (
    fund_id BIGINT,
    beneficiario_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fund_id, beneficiario_id),
    FOREIGN KEY (fund_id) REFERENCES funds(id),
    FOREIGN KEY (beneficiario_id) REFERENCES tipos_beneficiarios(id)
);

-- Tabla para regiones
CREATE TABLE IF NOT EXISTS regiones (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_region (descripcion)
);

-- Tabla de relación entre convocatorias y regiones
CREATE TABLE IF NOT EXISTS funds_regiones (
    fund_id BIGINT,
    region_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fund_id, region_id),
    FOREIGN KEY (fund_id) REFERENCES funds(id),
    FOREIGN KEY (region_id) REFERENCES regiones(id)
);

-- Tabla para instrumentos
CREATE TABLE IF NOT EXISTS instrumentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_instrumento (descripcion)
);

-- Tabla de relación entre convocatorias e instrumentos
CREATE TABLE IF NOT EXISTS funds_instrumentos (
    fund_id BIGINT,
    instrumento_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fund_id, instrumento_id),
    FOREIGN KEY (fund_id) REFERENCES funds(id),
    FOREIGN KEY (instrumento_id) REFERENCES instrumentos(id)
);

-- Tabla para fondos de financiación (FEDER, etc.)
CREATE TABLE IF NOT EXISTS fondos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_fondo (descripcion)
);

-- Tabla de relación entre convocatorias y fondos
CREATE TABLE IF NOT EXISTS funds_fondos (
    fund_id BIGINT,
    fondo_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fund_id, fondo_id),
    FOREIGN KEY (fund_id) REFERENCES funds(id),
    FOREIGN KEY (fondo_id) REFERENCES fondos(id)
);

-- Tabla para documentos
CREATE TABLE IF NOT EXISTS documentos (
    id BIGINT PRIMARY KEY,
    fund_id BIGINT NOT NULL,
    nombre_fichero VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tamano BIGINT,
    fecha_modificacion DATE,
    fecha_publicacion DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES funds(id)
);

-- Tabla para anuncios
CREATE TABLE IF NOT EXISTS anuncios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fund_id BIGINT NOT NULL,
    numero_anuncio VARCHAR(50),
    titulo TEXT NOT NULL,
    titulo_leng TEXT,
    texto TEXT,
    texto_leng TEXT,
    url VARCHAR(255),
    diario_oficial VARCHAR(200),
    fecha_publicacion DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES funds(id)
);

-- Tabla para detalles adicionales de la convocatoria
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

-- Índices adicionales para optimizar búsquedas
CREATE INDEX idx_funds_fecha_recepcion ON funds(fecha_recepcion);
CREATE INDEX idx_fund_details_fecha_fin ON fund_details(fecha_fin_solicitud);
CREATE INDEX idx_fund_details_abierto ON fund_details(abierto);
CREATE INDEX idx_fund_details_presupuesto ON fund_details(presupuesto_total);