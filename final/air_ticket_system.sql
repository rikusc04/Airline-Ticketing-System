-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: May 01, 2024 at 07:31 PM
-- Server version: 5.7.39
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `air_ticket_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `Airline`
--

CREATE TABLE `Airline` (
  `name` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Airline`
--

INSERT INTO `Airline` (`name`) VALUES
('American Airlines'),
('Delta'),
('Japan Airlines'),
('Jet Blue'),
('United Airlines');

-- --------------------------------------------------------

--
-- Table structure for table `Airline_Staff`
--

CREATE TABLE `Airline_Staff` (
  `username` varchar(20) NOT NULL,
  `password` varchar(300) NOT NULL,
  `first_name` varchar(15) NOT NULL,
  `last_name` varchar(15) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Airline_Staff`
--

INSERT INTO `Airline_Staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`) VALUES
('evan482', 'b29d2953c56077a5ef8b2ad193ec240f', 'Evan', 'Lee', '2004-04-11'),
('jefferson123', '482c811da5d5b4bc6d497ffa98491e38', 'Jefferson', 'Le', '2004-05-17'),
('rafiul456', '96b33694c4bb7dbd07391e0be54745fb', 'Rafiul', 'Kashfi', '2004-11-23'),
('soohyeuk789', '7d347cf0ee68174a3588f6cba31b8a67', 'Soohyeuk', 'Choi', '2004-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `Airline_Staff_Email_Address`
--

CREATE TABLE `Airline_Staff_Email_Address` (
  `username` varchar(20) NOT NULL,
  `email_address` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Airline_Staff_Email_Address`
--

INSERT INTO `Airline_Staff_Email_Address` (`username`, `email_address`) VALUES
('evan482', 'evan@nyu.edu'),
('jefferson123', 'jefferson@nyu.edu'),
('rafiul456', 'rafiul@nyu.edu'),
('soohyeuk789', 'soohyeuk@nyu.edu');

-- --------------------------------------------------------

--
-- Table structure for table `Airline_Staff_Phone_Number`
--

CREATE TABLE `Airline_Staff_Phone_Number` (
  `username` varchar(20) NOT NULL,
  `phone_number` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Airline_Staff_Phone_Number`
--

INSERT INTO `Airline_Staff_Phone_Number` (`username`, `phone_number`) VALUES
('evan482', '6198472289'),
('jefferson123', '3473477777'),
('rafiul456', '5167437777'),
('soohyeuk789', '9171726655');

-- --------------------------------------------------------

--
-- Table structure for table `Airplane`
--

CREATE TABLE `Airplane` (
  `airline_name` varchar(20) NOT NULL,
  `id_number` varchar(20) NOT NULL,
  `maintenance_id` varchar(20) DEFAULT NULL,
  `num_of_seat` int(11) NOT NULL,
  `manufacturing_company` varchar(20) NOT NULL,
  `model_number` varchar(20) NOT NULL,
  `manufacturing_date` date NOT NULL,
  `age` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Airplane`
--

INSERT INTO `Airplane` (`airline_name`, `id_number`, `maintenance_id`, `num_of_seat`, `manufacturing_company`, `model_number`, `manufacturing_date`, `age`) VALUES
('American Airlines', '65', 'B23432', 300, 'Boeing', '757', '2007-07-25', 16),
('Delta', '124', NULL, 150, 'Airbus', '827', '2010-03-23', 14),
('Jet Blue', '163', NULL, 250, 'Airbus', '737', '2011-03-23', 13),
('United Airlines', '165', 'C32052', 200, 'Boeing', '767', '2001-01-05', 23);

-- --------------------------------------------------------

--
-- Table structure for table `Airport`
--

CREATE TABLE `Airport` (
  `code` varchar(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  `city` varchar(15) NOT NULL,
  `country` varchar(15) NOT NULL,
  `number_of_terminals` decimal(8,0) NOT NULL,
  `type` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Airport`
--

INSERT INTO `Airport` (`code`, `name`, `city`, `country`, `number_of_terminals`, `type`) VALUES
('HND', 'Haneda Airport', 'Tokyo', 'Japan', '3', 'Both'),
('JFK', 'John F. Kennedy International Airport', 'NYC', 'USA', '8', 'Both'),
('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China', '5', 'Both');

-- --------------------------------------------------------

--
-- Table structure for table `Customer`
--

CREATE TABLE `Customer` (
  `email_address` varchar(30) NOT NULL,
  `first_name` varchar(15) NOT NULL,
  `last_name` varchar(15) NOT NULL,
  `password` varchar(300) NOT NULL,
  `building_number` int(11) NOT NULL,
  `street` varchar(20) NOT NULL,
  `apt_number` int(11) NOT NULL,
  `city` varchar(20) NOT NULL,
  `state` varchar(20) NOT NULL,
  `zipcode` int(11) NOT NULL,
  `passport_number` varchar(10) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(20) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Customer`
--

INSERT INTO `Customer` (`email_address`, `first_name`, `last_name`, `password`, `building_number`, `street`, `apt_number`, `city`, `state`, `zipcode`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('dh8493@nyu.edu', 'Dhruv', 'Gupta', '0ee81f7d0c7e18eff5672efce6dca1db', 193, 'silver', 307, 'Brooklyn', 'New York', 10010, 'M09423746', '2027-05-31', 'USA', '2004-01-01'),
('eb3210@nyu.edu', 'Ebtesham', 'Ahmed', '43b37a9eaaeb728bd57bcfe4b4fd21c0', 943, 'james', 434, 'Brooklyn', 'New York', 10010, 'M04323432', '2027-03-02', 'USA', '2004-01-05'),
('rs2910@nyu.edu', 'Riku', 'Santa Cruz', 'eb0de20156b7f34372aee76863711bab', 234, 'gold', 716, 'Brooklyn', 'New York', 10010, 'M30030293', '2028-07-23', 'USA', '2004-02-13'),
('sk8140@nyu.edu', 'Seha', 'Kim', 'e94166724b7af64a31c59973901c0a9c', 343, 'jay', 204, 'Brooklyn', 'New York', 10010, 'M30230212', '2029-03-29', 'USA', '1999-08-18');

-- --------------------------------------------------------

--
-- Table structure for table `CustomerPhone`
--

CREATE TABLE `CustomerPhone` (
  `email_address` varchar(30) NOT NULL,
  `phone_number` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `CustomerPhone`
--

INSERT INTO `CustomerPhone` (`email_address`, `phone_number`) VALUES
('dh8493@nyu.edu', '6193847756'),
('eb3210@nyu.edu', '9293514902'),
('rs2910@nyu.edu', '3474765116'),
('sk8140@nyu.edu', '3478967117');

-- --------------------------------------------------------

--
-- Table structure for table `Employed_By`
--

CREATE TABLE `Employed_By` (
  `airline_name` varchar(20) NOT NULL,
  `username` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Employed_By`
--

INSERT INTO `Employed_By` (`airline_name`, `username`) VALUES
('Delta', 'evan482'),
('United Airlines', 'jefferson123'),
('Delta', 'rafiul456'),
('Jet Blue', 'soohyeuk789');

-- --------------------------------------------------------

--
-- Table structure for table `Flight`
--

CREATE TABLE `Flight` (
  `airline_name` varchar(20) NOT NULL,
  `flight_number` varchar(5) NOT NULL,
  `depart_date` date NOT NULL,
  `depart_time` time NOT NULL,
  `depart_airport_code` varchar(10) NOT NULL,
  `arrival_date` date NOT NULL,
  `arrival_time` time NOT NULL,
  `arrival_airport_code` varchar(10) NOT NULL,
  `base_price` decimal(8,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `airplane_id_number` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Flight`
--

INSERT INTO `Flight` (`airline_name`, `flight_number`, `depart_date`, `depart_time`, `depart_airport_code`, `arrival_date`, `arrival_time`, `arrival_airport_code`, `base_price`, `status`, `airplane_id_number`) VALUES
('Delta', 'DL240', '2025-02-10', '16:09:08', 'JFK', '2025-02-10', '19:03:05', 'PVG', '980.20', 'delayed', NULL),
('Delta', 'DL241', '2025-02-17', '12:00:00', 'PVG', '2025-02-17', '03:30:00', 'JFK', '985.00', 'On time', NULL),
('Jet Blue', 'JB702', '2025-10-30', '08:12:03', 'PVG', '2025-10-31', '11:03:05', 'JFK', '985.00', 'On time', NULL),
('United Airlines', 'AA702', '2025-03-29', '03:02:03', 'HND', '2025-03-30', '06:03:05', 'JFK', '695.20', 'On time', NULL),
('United Airlines', 'AA703', '2025-04-10', '12:30:00', 'JFK', '2025-04-10', '04:13:00', 'HND', '715.00', 'delayed', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `Maintenance`
--

CREATE TABLE `Maintenance` (
  `id` varchar(20) NOT NULL,
  `start_date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_date` date NOT NULL,
  `end_time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Maintenance`
--

INSERT INTO `Maintenance` (`id`, `start_date`, `start_time`, `end_date`, `end_time`) VALUES
('B23432', '2024-03-02', '03:20:03', '2024-03-04', '14:20:32'),
('C32052', '2024-03-02', '03:20:03', '2024-03-04', '14:20:32');

-- --------------------------------------------------------

--
-- Table structure for table `Purchase`
--

CREATE TABLE `Purchase` (
  `id_number` varchar(20) NOT NULL,
  `email_address` varchar(30) NOT NULL,
  `purchase_time` time NOT NULL,
  `purchase_date` date NOT NULL,
  `card_type` varchar(30) NOT NULL,
  `card_number` varchar(30) NOT NULL,
  `name_on_card` varchar(20) NOT NULL,
  `expiration_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Purchase`
--

INSERT INTO `Purchase` (`id_number`, `email_address`, `purchase_time`, `purchase_date`, `card_type`, `card_number`, `name_on_card`, `expiration_date`) VALUES
('100', 'sk8140@nyu.edu', '07:30:00', '2024-12-20', 'debit', '1244 5677 8923 3456', 'Seha Kim', '2027-09-17'),
('101', 'sk8140@nyu.edu', '07:30:00', '2024-12-20', 'debit', '1244 5677 8923 3456', 'Seha Kim', '2027-09-17'),
('102', 'rs2910@nyu.edu', '07:30:00', '2024-12-20', 'debit', '1864 9107 6217 9651', 'Riku Santa Cruz', '2029-10-22'),
('103', 'eb3210@nyu.edu', '09:15:00', '2024-12-25', 'credit', '1056 9992 8760 9111', 'Ebtesham Ahmed', '2026-12-11'),
('104', 'eb3210@nyu.edu', '09:15:00', '2024-12-25', 'credit', '1056 9992 8760 9111', 'Ebtesham Ahmed', '2026-12-11');

-- --------------------------------------------------------

--
-- Table structure for table `Reviews`
--

CREATE TABLE `Reviews` (
  `email_address` varchar(20) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `flight_number` varchar(5) NOT NULL,
  `depart_date` date NOT NULL,
  `depart_time` time NOT NULL,
  `rating` decimal(2,1) NOT NULL,
  `comment` varchar(1000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Reviews`
--

INSERT INTO `Reviews` (`email_address`, `airline_name`, `flight_number`, `depart_date`, `depart_time`, `rating`, `comment`) VALUES
('eb3210@nyu.edu', 'Delta', 'DL240', '2025-02-10', '16:09:08', '3.2', 'The flight had too much turbulence!'),
('rs2910@nyu.edu', 'Delta', 'DL240', '2025-02-10', '16:09:08', '1.0', 'ter'),
('rs2910@nyu.edu', 'United Airlines', 'AA702', '2025-03-29', '03:02:03', '2.1', 'Terrible food! Must get better food!'),
('sk8140@nyu.edu', 'United Airlines', 'AA702', '2025-03-29', '03:02:03', '4.5', 'The flight was great!');

-- --------------------------------------------------------

--
-- Table structure for table `Ticket`
--

CREATE TABLE `Ticket` (
  `id_number` varchar(20) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `flight_number` varchar(5) NOT NULL,
  `depart_date` date NOT NULL,
  `depart_time` time NOT NULL,
  `sold_price` decimal(8,2) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Ticket`
--

INSERT INTO `Ticket` (`id_number`, `airline_name`, `flight_number`, `depart_date`, `depart_time`, `sold_price`, `first_name`, `last_name`, `date_of_birth`) VALUES
('100', 'United Airlines', 'AA702', '2025-03-29', '03:02:03', '999.00', 'Seha', 'Kim', '1999-08-18'),
('101', 'United Airlines', 'AA703', '2025-04-10', '12:30:00', '985.00', 'Seha', 'Kim', '1999-08-18'),
('102', 'United Airlines', 'AA702', '2025-03-29', '03:02:03', '999.00', 'Riku', 'Santa Cruz', '2004-02-13'),
('103', 'Delta', 'DL240', '2025-02-10', '16:09:08', '985.00', 'Ebtesham', 'Ahmed', '2004-01-05'),
('104', 'Delta', 'DL241', '2025-02-17', '12:00:00', '1000.00', 'Ebtesham', 'Ahmed', '2004-01-05');

-- --------------------------------------------------------

--
-- Table structure for table `Trips`
--

CREATE TABLE `Trips` (
  `trip_id` varchar(20) NOT NULL,
  `passenger_email` varchar(30) NOT NULL,
  `outbound_ticket_id` varchar(20) NOT NULL,
  `return_ticket_id` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Trips`
--

INSERT INTO `Trips` (`trip_id`, `passenger_email`, `outbound_ticket_id`, `return_ticket_id`) VALUES
('1', 'sk8140@nyu.edu', '100', '101'),
('2', 'rs2910@nyu.edu', '102', NULL),
('3', 'eb3210@nyu.edu', '103', '104');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Airline`
--
ALTER TABLE `Airline`
  ADD PRIMARY KEY (`name`);

--
-- Indexes for table `Airline_Staff`
--
ALTER TABLE `Airline_Staff`
  ADD PRIMARY KEY (`username`);

--
-- Indexes for table `Airline_Staff_Email_Address`
--
ALTER TABLE `Airline_Staff_Email_Address`
  ADD PRIMARY KEY (`username`);

--
-- Indexes for table `Airline_Staff_Phone_Number`
--
ALTER TABLE `Airline_Staff_Phone_Number`
  ADD PRIMARY KEY (`username`);

--
-- Indexes for table `Airplane`
--
ALTER TABLE `Airplane`
  ADD PRIMARY KEY (`airline_name`,`id_number`),
  ADD KEY `maintenance_id` (`maintenance_id`);

--
-- Indexes for table `Airport`
--
ALTER TABLE `Airport`
  ADD PRIMARY KEY (`code`);

--
-- Indexes for table `Customer`
--
ALTER TABLE `Customer`
  ADD PRIMARY KEY (`email_address`);

--
-- Indexes for table `CustomerPhone`
--
ALTER TABLE `CustomerPhone`
  ADD PRIMARY KEY (`email_address`,`phone_number`);

--
-- Indexes for table `Employed_By`
--
ALTER TABLE `Employed_By`
  ADD PRIMARY KEY (`airline_name`,`username`),
  ADD KEY `username` (`username`);

--
-- Indexes for table `Flight`
--
ALTER TABLE `Flight`
  ADD PRIMARY KEY (`airline_name`,`flight_number`,`depart_date`,`depart_time`),
  ADD KEY `depart_airport_code` (`depart_airport_code`),
  ADD KEY `arrival_airport_code` (`arrival_airport_code`);

--
-- Indexes for table `Maintenance`
--
ALTER TABLE `Maintenance`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Purchase`
--
ALTER TABLE `Purchase`
  ADD PRIMARY KEY (`id_number`,`email_address`),
  ADD KEY `email_address` (`email_address`);

--
-- Indexes for table `Reviews`
--
ALTER TABLE `Reviews`
  ADD PRIMARY KEY (`email_address`,`airline_name`,`flight_number`,`depart_date`,`depart_time`),
  ADD KEY `airline_name` (`airline_name`,`flight_number`,`depart_date`,`depart_time`);

--
-- Indexes for table `Ticket`
--
ALTER TABLE `Ticket`
  ADD PRIMARY KEY (`id_number`),
  ADD KEY `airline_name` (`airline_name`,`flight_number`,`depart_date`,`depart_time`);

--
-- Indexes for table `Trips`
--
ALTER TABLE `Trips`
  ADD PRIMARY KEY (`trip_id`),
  ADD KEY `outbound_ticket_id` (`outbound_ticket_id`),
  ADD KEY `return_ticket_id` (`return_ticket_id`),
  ADD KEY `passenger_email` (`passenger_email`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Trips`
--
ALTER TABLE `Trips`
  ADD CONSTRAINT `trips_ibfk_1` FOREIGN KEY (`outbound_ticket_id`) REFERENCES `Ticket` (`id_number`),
  ADD CONSTRAINT `trips_ibfk_2` FOREIGN KEY (`return_ticket_id`) REFERENCES `Ticket` (`id_number`),
  ADD CONSTRAINT `trips_ibfk_3` FOREIGN KEY (`passenger_email`) REFERENCES `Customer` (`email_address`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
