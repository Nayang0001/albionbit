-- ===========================
-- Servidores
-- ===========================

CREATE TABLE IF NOT EXISTS guilds (

    guild_id INTEGER PRIMARY KEY,
    nombre TEXT

);

-- ===========================
-- Jugadores
-- ===========================

CREATE TABLE IF NOT EXISTS players (

    discord_id INTEGER PRIMARY KEY,
    nombre TEXT

);

-- ===========================
-- Aventuras
-- ===========================

CREATE TABLE IF NOT EXISTS adventures (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    guild_id INTEGER,

    leader_id INTEGER,

    tipo TEXT,

    contenido TEXT,

    descripcion TEXT,

    estado TEXT DEFAULT 'abierta',

    mensaje_id INTEGER,

    canal_id INTEGER,

    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- ===========================
-- Roles de la aventura
-- ===========================

CREATE TABLE IF NOT EXISTS adventure_roles (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    adventure_id INTEGER,

    nombre TEXT,

    cantidad INTEGER,

    ocupados INTEGER DEFAULT 0

);

-- ===========================
-- Jugadores inscritos
-- ===========================

CREATE TABLE IF NOT EXISTS adventure_players (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    adventure_id INTEGER,

    discord_id INTEGER,

    rol TEXT,

    arma TEXT

);

-- ===========================
-- Registro de disponibilidad AFK
-- ===========================

CREATE TABLE IF NOT EXISTS afk_records (

    guild_id INTEGER NOT NULL,

    user_id INTEGER NOT NULL,

    user_name TEXT NOT NULL,

    reason TEXT NOT NULL,

    is_afk INTEGER NOT NULL DEFAULT 1,

    updated_by INTEGER NOT NULL,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (guild_id, user_id)

);

-- ===========================
-- Killboard
-- ===========================

CREATE TABLE IF NOT EXISTS killboard_tracked (

    guild_id INTEGER PRIMARY KEY,

    nombre TEXT,

    channel_kills INTEGER,

    channel_deaths INTEGER,

    albion_guild_id TEXT

);

CREATE TABLE IF NOT EXISTS killboard_events (

    event_id TEXT PRIMARY KEY,

    guild_id INTEGER,

    event_type TEXT,

    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
