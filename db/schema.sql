-- Airline Ticketing System — schema
-- Loaded once at DB init. Contains no user data and no plaintext passwords.
-- Passwords are bcrypt hashes generated at registration time (see app/security.py).

SET NAMES utf8mb4;
SET SQL_MODE = "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION";

START TRANSACTION;

-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Airline` (
  `name` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Airline_Staff` (
  `username` VARCHAR(20) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `first_name` VARCHAR(15) NOT NULL,
  `last_name` VARCHAR(15) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Airline_Staff_Email_Address` (
  `username` VARCHAR(20) NOT NULL,
  `email_address` VARCHAR(60) NOT NULL,
  PRIMARY KEY (`username`, `email_address`),
  CONSTRAINT `fk_staff_email_username`
    FOREIGN KEY (`username`) REFERENCES `Airline_Staff` (`username`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Airline_Staff_Phone_Number` (
  `username` VARCHAR(20) NOT NULL,
  `phone_number` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`username`, `phone_number`),
  CONSTRAINT `fk_staff_phone_username`
    FOREIGN KEY (`username`) REFERENCES `Airline_Staff` (`username`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Airport` (
  `code` VARCHAR(10) NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `city` VARCHAR(20) NOT NULL,
  `country` VARCHAR(20) NOT NULL,
  `number_of_terminals` INT NOT NULL,
  `type` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Maintenance` (
  `id` VARCHAR(20) NOT NULL,
  `start_date` DATE NOT NULL,
  `start_time` TIME NOT NULL,
  `end_date` DATE NOT NULL,
  `end_time` TIME NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Airplane` (
  `airline_name` VARCHAR(20) NOT NULL,
  `id_number` VARCHAR(20) NOT NULL,
  `maintenance_id` VARCHAR(20) DEFAULT NULL,
  `num_of_seat` INT NOT NULL,
  `manufacturing_company` VARCHAR(20) NOT NULL,
  `model_number` VARCHAR(20) NOT NULL,
  `manufacturing_date` DATE NOT NULL,
  `age` INT NOT NULL,
  PRIMARY KEY (`airline_name`, `id_number`),
  KEY `idx_airplane_maintenance` (`maintenance_id`),
  CONSTRAINT `fk_airplane_airline`
    FOREIGN KEY (`airline_name`) REFERENCES `Airline` (`name`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_airplane_maintenance`
    FOREIGN KEY (`maintenance_id`) REFERENCES `Maintenance` (`id`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Customer` (
  `email_address` VARCHAR(60) NOT NULL,
  `first_name` VARCHAR(30) NOT NULL,
  `last_name` VARCHAR(30) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `building_number` INT NOT NULL,
  `street` VARCHAR(30) NOT NULL,
  `apt_number` INT NOT NULL,
  `city` VARCHAR(30) NOT NULL,
  `state` VARCHAR(30) NOT NULL,
  `zipcode` INT NOT NULL,
  `passport_number` VARCHAR(20) NOT NULL,
  `passport_expiration` DATE NOT NULL,
  `passport_country` VARCHAR(30) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  PRIMARY KEY (`email_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `CustomerPhone` (
  `email_address` VARCHAR(60) NOT NULL,
  `phone_number` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`email_address`, `phone_number`),
  CONSTRAINT `fk_customerphone_customer`
    FOREIGN KEY (`email_address`) REFERENCES `Customer` (`email_address`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Employed_By` (
  `airline_name` VARCHAR(20) NOT NULL,
  `username` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`airline_name`, `username`),
  KEY `idx_employed_username` (`username`),
  CONSTRAINT `fk_employed_airline`
    FOREIGN KEY (`airline_name`) REFERENCES `Airline` (`name`),
  CONSTRAINT `fk_employed_username`
    FOREIGN KEY (`username`) REFERENCES `Airline_Staff` (`username`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Flight` (
  `airline_name` VARCHAR(20) NOT NULL,
  `flight_number` VARCHAR(5) NOT NULL,
  `depart_date` DATE NOT NULL,
  `depart_time` TIME NOT NULL,
  `depart_airport_code` VARCHAR(10) NOT NULL,
  `arrival_date` DATE NOT NULL,
  `arrival_time` TIME NOT NULL,
  `arrival_airport_code` VARCHAR(10) NOT NULL,
  `base_price` DECIMAL(8,2) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  `airplane_id_number` VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY (`airline_name`, `flight_number`, `depart_date`, `depart_time`),
  KEY `idx_flight_depart_airport` (`depart_airport_code`),
  KEY `idx_flight_arrival_airport` (`arrival_airport_code`),
  CONSTRAINT `fk_flight_airline`
    FOREIGN KEY (`airline_name`) REFERENCES `Airline` (`name`),
  CONSTRAINT `fk_flight_depart_airport`
    FOREIGN KEY (`depart_airport_code`) REFERENCES `Airport` (`code`),
  CONSTRAINT `fk_flight_arrival_airport`
    FOREIGN KEY (`arrival_airport_code`) REFERENCES `Airport` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Ticket` (
  `id_number` VARCHAR(20) NOT NULL,
  `airline_name` VARCHAR(20) NOT NULL,
  `flight_number` VARCHAR(5) NOT NULL,
  `depart_date` DATE NOT NULL,
  `depart_time` TIME NOT NULL,
  `sold_price` DECIMAL(8,2) NOT NULL,
  `first_name` VARCHAR(30) NOT NULL,
  `last_name` VARCHAR(30) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  PRIMARY KEY (`id_number`),
  KEY `idx_ticket_flight` (`airline_name`, `flight_number`, `depart_date`, `depart_time`),
  CONSTRAINT `fk_ticket_flight`
    FOREIGN KEY (`airline_name`, `flight_number`, `depart_date`, `depart_time`)
    REFERENCES `Flight` (`airline_name`, `flight_number`, `depart_date`, `depart_time`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- NOTE ON PAYMENT DATA:
-- We only store the LAST 4 DIGITS of the card. Storing full PANs is a PCI-DSS
-- violation. For a real deployment, delete `card_last4` and switch to a
-- payment processor token (Stripe, Braintree, etc).
CREATE TABLE IF NOT EXISTS `Purchase` (
  `id_number` VARCHAR(20) NOT NULL,
  `email_address` VARCHAR(60) NOT NULL,
  `purchase_time` TIME NOT NULL,
  `purchase_date` DATE NOT NULL,
  `card_type` VARCHAR(30) NOT NULL,
  `card_last4` CHAR(4) NOT NULL,
  `name_on_card` VARCHAR(30) NOT NULL,
  `expiration_date` DATE NOT NULL,
  PRIMARY KEY (`id_number`, `email_address`),
  KEY `idx_purchase_email` (`email_address`),
  CONSTRAINT `fk_purchase_ticket`
    FOREIGN KEY (`id_number`) REFERENCES `Ticket` (`id_number`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_purchase_customer`
    FOREIGN KEY (`email_address`) REFERENCES `Customer` (`email_address`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Reviews` (
  `email_address` VARCHAR(60) NOT NULL,
  `airline_name` VARCHAR(20) NOT NULL,
  `flight_number` VARCHAR(5) NOT NULL,
  `depart_date` DATE NOT NULL,
  `depart_time` TIME NOT NULL,
  `rating` DECIMAL(3,1) NOT NULL,
  `comment` VARCHAR(1000) DEFAULT NULL,
  PRIMARY KEY (`email_address`, `airline_name`, `flight_number`, `depart_date`, `depart_time`),
  KEY `idx_reviews_flight` (`airline_name`, `flight_number`, `depart_date`, `depart_time`),
  CONSTRAINT `fk_reviews_customer`
    FOREIGN KEY (`email_address`) REFERENCES `Customer` (`email_address`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_reviews_flight`
    FOREIGN KEY (`airline_name`, `flight_number`, `depart_date`, `depart_time`)
    REFERENCES `Flight` (`airline_name`, `flight_number`, `depart_date`, `depart_time`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Trips` (
  `trip_id` VARCHAR(36) NOT NULL,
  `passenger_email` VARCHAR(60) NOT NULL,
  `outbound_ticket_id` VARCHAR(20) NOT NULL,
  `return_ticket_id` VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY (`trip_id`),
  KEY `idx_trips_outbound` (`outbound_ticket_id`),
  KEY `idx_trips_return` (`return_ticket_id`),
  KEY `idx_trips_email` (`passenger_email`),
  CONSTRAINT `fk_trips_outbound`
    FOREIGN KEY (`outbound_ticket_id`) REFERENCES `Ticket` (`id_number`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_trips_return`
    FOREIGN KEY (`return_ticket_id`) REFERENCES `Ticket` (`id_number`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_trips_customer`
    FOREIGN KEY (`passenger_email`) REFERENCES `Customer` (`email_address`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Reference data (safe to ship): airlines and sample airports so new staff
-- accounts can register against a known airline out of the box.

INSERT IGNORE INTO `Airline` (`name`) VALUES
  ('American Airlines'),
  ('Delta'),
  ('Japan Airlines'),
  ('Jet Blue'),
  ('United Airlines');

INSERT IGNORE INTO `Airport` (`code`, `name`, `city`, `country`, `number_of_terminals`, `type`) VALUES
  ('HND', 'Haneda Airport', 'Tokyo', 'Japan', 3, 'Both'),
  ('JFK', 'John F. Kennedy International Airport', 'NYC', 'USA', 8, 'Both'),
  ('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China', 5, 'Both');

COMMIT;
