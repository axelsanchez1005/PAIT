-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 06-02-2026 a las 03:14:18
-- Versión del servidor: 9.2.0
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
-- Estructura de tabla para la tabla `equipos`
--

CREATE TABLE `equipos` (
  `id` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `idea` text NOT NULL,
  `id_lider` int NOT NULL,
  `id_mentor` int DEFAULT NULL,
  `link_whatsapp` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `equipos`
--

INSERT INTO `equipos` (`id`, `nombre`, `idea`, `id_lider`, `id_mentor`, `link_whatsapp`) VALUES
(1, 'PAIT - Equipo 1', 'Prueba', 1, NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `invitaciones`
--

CREATE TABLE `invitaciones` (
  `id` int NOT NULL,
  `id_emisor` int NOT NULL,
  `id_receptor` int NOT NULL,
  `id_equipo` int NOT NULL,
  `tipo` enum('INVITAR','SOLICITAR') NOT NULL,
  `estado` enum('PENDIENTE','ACEPTADA','RECHAZADA') DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
-- Estructura de tabla para la tabla `miembros_equipo`
--

CREATE TABLE `miembros_equipo` (
  `id_equipo` int NOT NULL,
  `id_usuario` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `miembros_equipo`
--

INSERT INTO `miembros_equipo` (`id_equipo`, `id_usuario`) VALUES
(1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int NOT NULL,
  `codigo` int NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('U','M','A') NOT NULL COMMENT 'U=Alumno, M=Mentor',
  `correo` varchar(255) DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `carrera` varchar(10) DEFAULT NULL,
  `grado` int DEFAULT NULL,
  `grupo` char(1) DEFAULT NULL,
  `turno` enum('M','V') DEFAULT NULL,
  `ingreso` datetime DEFAULT NULL,
  `invitados` int DEFAULT '0',
  `presentacion` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `codigo`, `nombre`, `password`, `rol`, `correo`, `celular`, `carrera`, `grado`, `grupo`, `turno`, `ingreso`, `invitados`, `presentacion`) VALUES
(1, 222910051, 'SANCHEZ HERNANDEZ AXEL GILBERTO', 'scrypt:32768:8:1$B9ExGPuhbkc4HFHz$b6784a61489a2e22b23b1484d2bf698f9b8f7c38d4a335deb5c1026276ee7f033d97246c35ee5c95603c57f063a1636e58976a086ba27ad528d438eb138347aa', 'U', 'axel.sanchez1005@alumnos.udg.mx', '3321793454', 'TPIN', 8, 'A', 'M', '2026-02-04 15:49:05', 0, NULL),
(2, 8903727, 'GONZALES PEÑANIETO JOSE PEPE', 'polomatute', 'M', 'jose.gonzales1044@academicos.udg.mx', '1321780000', NULL, NULL, NULL, NULL, NULL, 0, NULL),
(3, 222910052, 'juan', 'polimatute', 'A', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `equipos`
--
ALTER TABLE `equipos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_lider` (`id_lider`),
  ADD KEY `id_mentor` (`id_mentor`);

--
-- Indices de la tabla `invitaciones`
--
ALTER TABLE `invitaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_emisor` (`id_emisor`),
  ADD KEY `id_receptor` (`id_receptor`),
  ADD KEY `id_equipo` (`id_equipo`);

--
-- Indices de la tabla `mentores`
--
ALTER TABLE `mentores`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `miembros_equipo`
--
ALTER TABLE `miembros_equipo`
  ADD PRIMARY KEY (`id_equipo`,`id_usuario`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `equipos`
--
ALTER TABLE `equipos`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `invitaciones`
--
ALTER TABLE `invitaciones`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

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

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `equipos`
--
ALTER TABLE `equipos`
  ADD CONSTRAINT `equipos_ibfk_1` FOREIGN KEY (`id_lider`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `equipos_ibfk_2` FOREIGN KEY (`id_mentor`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `invitaciones`
--
ALTER TABLE `invitaciones`
  ADD CONSTRAINT `invitaciones_ibfk_1` FOREIGN KEY (`id_emisor`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `invitaciones_ibfk_2` FOREIGN KEY (`id_receptor`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `invitaciones_ibfk_3` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id`);

--
-- Filtros para la tabla `miembros_equipo`
--
ALTER TABLE `miembros_equipo`
  ADD CONSTRAINT `miembros_equipo_ibfk_1` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `miembros_equipo_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
