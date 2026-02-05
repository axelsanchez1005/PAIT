-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 05-02-2026 a las 02:41:50
-- Versión del servidor: 8.0.44
-- Versión de PHP: 7.4.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `pait`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alumnos`
--

CREATE TABLE `alumnos` (
  `codigoAl` int NOT NULL,
  `nombreAl` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `passwordAl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `carrera` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `grado` int NOT NULL,
  `grupo` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `turno` enum('M','V') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `ingreso` datetime(6) NOT NULL,
  `invitados` int NOT NULL,
  `celularAl` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `alumnos`
--

INSERT INTO `alumnos` (`codigoAl`, `nombreAl`, `passwordAl`, `carrera`, `grado`, `grupo`, `turno`, `ingreso`, `invitados`, `celularAl`) VALUES
(222910051, 'SANCHEZ HERNANDEZ AXEL GILBERTO', 'polimatute', 'TPIN', 8, 'A', 'M', '2026-02-04 15:49:05.000000', 0, '3321790000');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mentores`
--

CREATE TABLE `mentores` (
  `id` int NOT NULL,
  `codigoMe` int NOT NULL,
  `nombreMe` varchar(100) NOT NULL,
  `passwordMe` varchar(255) NOT NULL,
  `correoMe` varchar(255) NOT NULL,
  `celularMe` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `mentores`
--

INSERT INTO `mentores` (`id`, `codigoMe`, `nombreMe`, `passwordMe`, `correoMe`, `celularMe`) VALUES
(1, 8903727, 'GONZALES PEÑANIETO JOSE PEPE', 'polomatute', 'jose.gonzales1044@academicos.udg.mx', '1321780000');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int NOT NULL,
  `codigo` int NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('U','M') NOT NULL COMMENT 'U=Alumno, M=Mentor',
  `correo` varchar(255) DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `carrera` varchar(10) DEFAULT NULL,
  `grado` int DEFAULT NULL,
  `grupo` char(1) DEFAULT NULL,
  `turno` enum('M','V') DEFAULT NULL,
  `ingreso` datetime DEFAULT NULL,
  `invitados` int DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `codigo`, `nombre`, `password`, `rol`, `correo`, `celular`, `carrera`, `grado`, `grupo`, `turno`, `ingreso`, `invitados`) VALUES
(1, 222910051, 'SANCHEZ HERNANDEZ AXEL GILBERTO', 'scrypt:32768:8:1$ARbWz1oHfOmMSGhO$6965bb423954b35628f8b5206963c02c4efa5c3d682fd12d9b937d75fe3ea7494223ccf4a07608a207c56b6c7b4ef41b883ea0c297e2a45028fed00f3ccdee16', 'U', 'julian.mayorga0959@alumnos.udg.mx', '3321790000', 'TPIN', 8, 'A', 'M', '2026-02-04 15:49:05', 0),
(2, 8903727, 'GONZALES PEÑANIETO JOSE PEPE', 'polomatute', 'M', 'jose.gonzales1044@academicos.udg.mx', '1321780000', NULL, NULL, NULL, NULL, NULL, 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `mentores`
--
ALTER TABLE `mentores`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `mentores`
--
ALTER TABLE `mentores`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
