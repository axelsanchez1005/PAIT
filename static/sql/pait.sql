-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 14-02-2026 a las 03:08:37
-- Versión del servidor: 9.2.0
-- Versión de PHP: 7.4.9
--HOLA

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
(222910051, 'SANCHEZ HERNANDEZ AXEL GILBERTO', 'polimatute', 'TPIN', 8, 'A', 'M', '2026-02-04 15:49:05.000000', 0, '3321790000'),
(4, 'TERRANOVA HERNANDEZ DIEGO KALO', 'polimatute', 'TPBI', 5, 'A', 'M', '2026-02-07 21:23:10.000000', 0, '3321793455');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `anuncios`
--

CREATE TABLE `anuncios` (
  `id` int NOT NULL,
  `id_equipo` int DEFAULT NULL,
  `id_usuario` int NOT NULL,
  `contenido` text NOT NULL,
  `fecha_publicacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fijado` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `anuncios`
--

INSERT INTO `anuncios` (`id`, `id_equipo`, `id_usuario`, `contenido`, `fecha_publicacion`, `fijado`) VALUES
(1, 1, 2, 'HOLA GUAPOS', '2026-02-07 21:52:42', 0),
(7, NULL, 3, 'yy', '2026-02-08 01:55:44', 0),
(12, NULL, 3, 'h', '2026-02-08 02:27:16', 0),
(13, NULL, 3, 'o\r\n', '2026-02-08 02:27:20', 0),
(14, NULL, 3, 'l', '2026-02-08 02:27:32', 0),
(16, 1, 2, 'hola', '2026-02-13 02:16:34', 0),
(17, 1, 2, 'Hola cómo están\r\n', '2026-02-13 14:17:05', 0);

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
  `link_whatsapp` varchar(255) DEFAULT NULL,
  `busca_carrera` varchar(10) DEFAULT 'Cualquiera',
  `busca_grado` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `equipos`
--

INSERT INTO `equipos` (`id`, `nombre`, `idea`, `id_lider`, `id_mentor`, `link_whatsapp`, `busca_carrera`, `busca_grado`) VALUES
(1, 'PAIT - Equipo 1', 'Prueba', 1, 2, 'https://whatsapp.com', 'TPEA', 6);

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

--
-- Volcado de datos para la tabla `invitaciones`
--

INSERT INTO `invitaciones` (`id`, `id_emisor`, `id_receptor`, `id_equipo`, `tipo`, `estado`) VALUES
(1, 4, 1, 1, 'SOLICITAR', 'RECHAZADA'),
(2, 1, 4, 1, 'INVITAR', 'ACEPTADA'),
(3, 4, 1, 1, 'SOLICITAR', 'ACEPTADA'),
(4, 4, 1, 1, 'SOLICITAR', 'ACEPTADA');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lecturas_anuncios`
--

CREATE TABLE `lecturas_anuncios` (
  `id_usuario` int NOT NULL,
  `id_anuncio` int NOT NULL,
  `fecha_lectura` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `lecturas_anuncios`
--

INSERT INTO `lecturas_anuncios` (`id_usuario`, `id_anuncio`, `fecha_lectura`) VALUES
(1, 1, '2026-02-08 00:20:53'),
(1, 14, '2026-02-08 02:28:28'),
(2, 14, '2026-02-08 03:07:31'),
(2, 16, '2026-02-13 18:36:12'),
(2, 17, '2026-02-13 18:36:10'),
(4, 14, '2026-02-13 18:41:20');

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
(1, 1),
(1, 2),
(1, 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int NOT NULL,
  `codigo` int NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('U','M','A') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'U=Alumno, M=Mentor',
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
(2, 222910052, 'GONZALES PEÑANIETO JOSE PEPE', 'scrypt:32768:8:1$PeMuo7eQLtxpPiBK$1ecf664cc99552ecace63d7199c7678f601096ebaa8643e3e547f78581e93257e39639e91fd418c473e998753cfee7e7aa25733606d04c71ef23b046b9bf366c', 'M', 'axelgilb2016@gmail.com', '1321780000', NULL, NULL, NULL, NULL, NULL, 0, NULL),
(3, 222910053, 'PEREZ HERNANDEZ CARLOS TRUJILLO', 'scrypt:32768:8:1$ceRvggj5shwfPfE5$a1980475193318b257ae0c7284a6cafbd7569d31153f2df11f32c7e97f93c05a6eb0abe8a378967cffdfab8d6cb9b55f055757ac657d38fbbc506e1808329bee', 'A', 'correfalso@gmail.com', 'NULL', 'NULL', 0, 'A', 'M', '2026-02-04 15:49:05', 0, 'ADMIN'),
(4, 222910054, 'TERRANOVA HERNANDEZ DIEGO KALO', 'scrypt:32768:8:1$sWd7e11XazdZCa0C$648abf88ae78c3e26d1d60edb5f0b867189add4c511e3b5cb3342597cd74e3d14e8802828fd39f2e021b4b48eaa3226e94206002f47721e1a7b57e16a0cf5d6f', 'U', 'correo@gmail.com', '3321793454', 'TPBI', 5, 'A', 'M', '2026-02-07 21:23:10', 0, 'hoaaa');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `anuncios`
--
ALTER TABLE `anuncios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_equipo` (`id_equipo`),
  ADD KEY `id_usuario` (`id_usuario`);

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
-- Indices de la tabla `lecturas_anuncios`
--
ALTER TABLE `lecturas_anuncios`
  ADD PRIMARY KEY (`id_usuario`,`id_anuncio`),
  ADD KEY `id_anuncio` (`id_anuncio`);

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
-- AUTO_INCREMENT de la tabla `anuncios`
--
ALTER TABLE `anuncios`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `equipos`
--
ALTER TABLE `equipos`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `invitaciones`
--
ALTER TABLE `invitaciones`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `mentores`
--
ALTER TABLE `mentores`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `anuncios`
--
ALTER TABLE `anuncios`
  ADD CONSTRAINT `anuncios_ibfk_1` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `anuncios_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

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
-- Filtros para la tabla `lecturas_anuncios`
--
ALTER TABLE `lecturas_anuncios`
  ADD CONSTRAINT `lecturas_anuncios_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `lecturas_anuncios_ibfk_2` FOREIGN KEY (`id_anuncio`) REFERENCES `anuncios` (`id`) ON DELETE CASCADE;

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
