# AZTU Turnstile Backend

## Database Setup

### Create Tables (PostgreSQL)

```sql
CREATE TABLE auth (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);

CREATE TABLE groups (
    id         SERIAL PRIMARY KEY,
    group_id   INTEGER NOT NULL UNIQUE,
    group      VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE positions (
    id          SERIAL PRIMARY KEY,
    position_id INTEGER NOT NULL UNIQUE,
    position    VARCHAR NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE "user" (
    id             SERIAL PRIMARY KEY,
    card_no        VARCHAR NOT NULL,
    name           VARCHAR NOT NULL,
    surname        VARCHAR NOT NULL,
    father_name    VARCHAR,
    fin_code       VARCHAR(7),
    gender         INTEGER NOT NULL,
    identification VARCHAR NOT NULL UNIQUE,
    group_number   VARCHAR,
    "group"        INTEGER,
    position       INTEGER,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT check_gender CHECK (gender IN (0, 1, 2))
);

CREATE TABLE user_access (
    id                   VARCHAR(256),
    employee_id          VARCHAR(256),
    access_date_time     VARCHAR(256),
    access_date          VARCHAR(256),
    access_time          VARCHAR(256),
    device_name          VARCHAR(256),
    device_serial_number VARCHAR(256),
    person_name          VARCHAR(256),
    card_no              VARCHAR(256),
    direction            VARCHAR(256)
);
```
