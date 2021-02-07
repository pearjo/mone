-- Copyright (C) 2020  Joe Pearson
--
-- This file is part of Mone.
--
-- Mone is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- Mone is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- Initialize the database.
-- Don't do anything if the database is not empty.

CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
  id TEXT NOT NULL,
  -- user_id INTEGER NOT NULL,
  json_data TEXT NOT NULL
  -- FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS budgets (
  id TEXT NOT NULL,
  -- user_id INTEGER NOT NULL,
  json_data TEXT NOT NULL
  -- FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS transactions (
  id TEXT NOT NULL,
  -- user_id INTEGER NOT NULL,
  json_data TEXT NOT NULL
  -- FOREIGN KEY (user_id) REFERENCES user (id)
);
