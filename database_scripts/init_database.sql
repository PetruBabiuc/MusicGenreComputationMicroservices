CREATE DATABASE licenta;

CREATE USER 'petru-admin'@'0.0.0.0' IDENTIFIED BY 'petru-admin';
GRANT ALL PRIVILEGES ON licenta.* TO 'petru-admin'@'0.0.0.0' WITH GRANT OPTION;

CREATE USER 'crud_user'@'0.0.0.0' IDENTIFIED BY 'crud_user_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON licenta.* TO 'crud_user'@'0.0.0.0' WITH GRANT OPTION;

FLUSH PRIVILEGES;