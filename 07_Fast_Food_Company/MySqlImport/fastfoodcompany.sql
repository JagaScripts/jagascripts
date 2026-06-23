CREATE DATABASE  IF NOT EXISTS `u110269477_fastfoodcompan` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `u110269477_fastfoodcompan`;
-- MySQL dump 10.13  Distrib 5.5.16, for Win32 (x86)
--
-- Host: localhost    Database: fastfoodcompany
-- ------------------------------------------------------
-- Server version	5.5.27-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categoria` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `imagen` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (7,'Café','045-coffee-machine.png'),(8,'Infusiones','040-coffee-cup.png'),(9,'Refrescos','012-cola.png'),(10,'Menús','029-package.png'),(11,'Postres y helados','027-donut.png'),(12,'Carta','047-menu.png');
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cliente` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `primer_apellido` varchar(45) NOT NULL,
  `segundo_apellido` varchar(45) NOT NULL,
  `dni` varchar(9) DEFAULT NULL,
  `direccion` varchar(300) DEFAULT NULL,
  `habitual` binary(1) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Jose Antonio','González','Alcántara','24377895B','Calle - Ramon Llull - 14 - 0 - 0 - 43895 - L\'ampolla - Tarragona - España','0'),(2,'Esther','Palomares','Callén','47622851V','Calle - Ramon Llull - 14 - 0 - 0 - 43895 - L\'Ampolla - Tarragona - España','0'),(5,'Por Defecto','No habitual','Nulo',NULL,NULL,NULL);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `descuento`
--

DROP TABLE IF EXISTS `descuento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `descuento` (
  `clave` varchar(300) NOT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `cliente_id_cliente` int(11) NOT NULL,
  `caducidad` varchar(45) NOT NULL,
  PRIMARY KEY (`clave`),
  KEY `fk_descuento_cliente_idx` (`cliente_id_cliente`),
  CONSTRAINT `fk_descuento_cliente` FOREIGN KEY (`cliente_id_cliente`) REFERENCES `cliente` (`id_cliente`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `descuento`
--

LOCK TABLES `descuento` WRITE;
/*!40000 ALTER TABLE `descuento` DISABLE KEYS */;
INSERT INTO `descuento` VALUES ('gr004956nujdve37',2,1,'20/06/2019');
/*!40000 ALTER TABLE `descuento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_venta_producto`
--

DROP TABLE IF EXISTS `detalle_venta_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detalle_venta_producto` (
  `producto_id_producto` int(11) NOT NULL,
  `venta_numero_venta` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_venta` float DEFAULT NULL,
  PRIMARY KEY (`producto_id_producto`,`venta_numero_venta`),
  KEY `fk_producto_has_venta_venta1_idx` (`venta_numero_venta`),
  KEY `fk_producto_has_venta_producto1_idx` (`producto_id_producto`),
  CONSTRAINT `fk_producto_has_venta_producto1` FOREIGN KEY (`producto_id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_producto_has_venta_venta1` FOREIGN KEY (`venta_numero_venta`) REFERENCES `venta` (`numero_venta`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_venta_producto`
--

LOCK TABLES `detalle_venta_producto` WRITE;
/*!40000 ALTER TABLE `detalle_venta_producto` DISABLE KEYS */;
INSERT INTO `detalle_venta_producto` VALUES (1,7,1,1.1),(1,9,1,1.1),(1,10,1,1.1),(1,14,1,1.1),(1,15,1,1.1),(1,17,1,1.1),(1,18,1,1.1),(1,21,1,1.1),(1,22,1,1.1),(1,23,1,1.1),(1,24,1,1.1),(1,25,10,11),(1,27,1,1.1),(1,29,1,1.1),(1,30,18,19.8),(1,32,3,3.3),(1,33,2,2.2),(1,34,1,1.1),(1,36,1,1.1),(2,10,1,1.2),(2,14,1,1.2),(2,15,1,1.2),(2,17,1,1.2),(2,18,1,1.2),(2,30,9,10.8),(2,32,30,36),(2,33,1,1.2),(2,34,1,1.2),(2,36,3,3.6),(3,6,1,1.3),(3,9,1,1.3),(3,14,1,1.3),(3,18,1,1.3),(3,25,1,1.3),(3,27,1,1.3),(3,30,1,1.3),(3,34,2,2.6),(4,8,1,1.3),(9,12,1,1.3),(10,12,1,1.5),(11,12,1,1.7),(11,35,1,1.7),(13,12,1,1.7),(16,6,1,4.9),(16,12,1,4.9),(16,32,1,4.9),(17,7,1,6.9),(17,32,2,13.8),(17,35,1,6.9),(18,7,1,3.9),(21,8,1,1.2),(42,8,1,1.1),(52,25,1,1.7);
/*!40000 ALTER TABLE `detalle_venta_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producto` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `precio` float NOT NULL,
  `imagen` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (1,'Café solo',1.1,'009-coffee.png'),(2,'Café cortado',1.2,'009-coffee.png'),(3,'Café con leche',1.3,'009-coffee.png'),(4,'Té negro',1.2,'002-tea.png'),(5,'Té rojo',1.2,'002-tea.png'),(6,'Té verde',1.2,'002-tea.png'),(7,'Manzanilla',1.1,'002-tea.png'),(8,'Poleo menta',1.1,'002-tea.png'),(9,'Cola pequeña',1.3,'005-cola-1.png'),(10,'Cola mediana',1.5,'005-cola-1.png'),(11,'Cola grande',1.7,'005-cola-1.png'),(12,'Cerveza pequeña',1.5,'042-beer.png'),(13,'Cerveza grande',1.7,'042-beer.png'),(14,'Cerveza mediana',1.9,'042-beer.png'),(15,'Menú burguer pequeño',3.9,'006-burger-2.png'),(16,'Menú burguer mediano',4.9,'006-burger-2.png'),(17,'Menú burguer grande',6.9,'006-burger-2.png'),(18,'Menú patatas pequeño',3.9,'050-french-fries.png'),(19,'Menú patatas mediano',4.9,'050-french-fries.png'),(20,'Menú patatas grande',5.9,'050-french-fries.png'),(21,'Cruasán',1.8,'017-croissant.png'),(22,'Gofre',1.9,'041-waffle.png'),(23,'Tallarines tres delicias',4.75,'046-noodles.png'),(24,'Batido de fresa',1.8,'013-milkshake.png'),(25,'Batido de chocolate',1.8,'013-milkshake.png'),(26,'Helado de fresa',1.5,'026-ice-cream.png'),(27,'Helado de vainilla',1.5,'026-ice-cream.png'),(28,'Helado de chocolate',1.5,'026-ice-cream.png'),(29,'Cucurucho helado fresa',1.5,'011-ice-cream-1.png'),(30,'Cucurucho helado chocolate',1.5,'011-ice-cream-1.png'),(31,'Cucurucho helado vainilla',1.5,'011-ice-cream-1.png'),(32,'Patatas friatas pequeñas',2.9,'008-fried-potatoes.png'),(33,'Patatas fritas medianas',2.9,'008-fried-potatoes.png'),(34,'Patatas fritas grandes',3.9,'008-fried-potatoes.png'),(35,'Pierna de pollo',2.5,'016-chicken-leg-1.png'),(36,'Muslo de pollo',3.5,'043-chicken-leg.png'),(37,'Pollo frito',5.7,'021-fried-chicken.png'),(38,'Kebab durum',3.75,'030-kebab.png'),(39,'Kebab pita',5.65,'030-kebab.png'),(40,'Pizza atún',2.9,'023-pizza-slice.png'),(41,'Pizza bacon',2.9,'023-pizza-slice.png'),(42,'Donut chocolate',1.9,'027-donut.png'),(43,'Ensalada',1.9,'028-rice.png'),(44,'Entrecot',17.9,'025-meat.png'),(45,'Huevos fritos',5.9,'020-fried-egg.png'),(46,'Salchicchas',7.9,'019-sausage.png'),(47,'Queso',1.9,'018-cheese.png'),(48,'Hot dog',2.9,'015-hot-dog-1.png'),(49,'Burguer bacon',1.9,'010-burger.png'),(50,'Burguer ',1.5,'010-burger.png'),(51,'Donut',1.6,'027-donut.png'),(52,'Café con hielo',1.7,'009-coffee.png'),(53,'producto de prueba',1.8,'SecurityAndMaintenance_Alert.png');
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_pertenece_categoria`
--

DROP TABLE IF EXISTS `producto_pertenece_categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producto_pertenece_categoria` (
  `categoria_id_categoria` int(11) NOT NULL,
  `producto_id_producto` int(11) NOT NULL,
  PRIMARY KEY (`categoria_id_categoria`,`producto_id_producto`),
  KEY `fk_categoria_has_producto_producto1_idx` (`producto_id_producto`),
  KEY `fk_categoria_has_producto_categoria1_idx` (`categoria_id_categoria`),
  CONSTRAINT `fk_categoria_has_producto_categoria10` FOREIGN KEY (`categoria_id_categoria`) REFERENCES `categoria` (`id_categoria`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_categoria_has_producto_producto10` FOREIGN KEY (`producto_id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_pertenece_categoria`
--

LOCK TABLES `producto_pertenece_categoria` WRITE;
/*!40000 ALTER TABLE `producto_pertenece_categoria` DISABLE KEYS */;
INSERT INTO `producto_pertenece_categoria` VALUES (7,1),(7,2),(7,3),(8,4),(8,5),(8,6),(8,7),(8,8),(9,9),(9,10),(9,11),(9,12),(9,13),(9,14),(10,15),(10,16),(10,17),(10,18),(10,19),(10,20),(11,21),(11,22),(11,24),(11,25),(11,26),(11,27),(11,28),(11,29),(11,30),(11,31),(12,32),(12,33),(12,34),(12,35),(12,36),(12,37),(12,38),(12,39),(12,40),(12,41),(11,42),(12,42),(12,43),(12,44),(12,45),(12,46),(12,47),(12,48),(12,49),(12,50),(11,51),(7,52),(7,53);
/*!40000 ALTER TABLE `producto_pertenece_categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta`
--

DROP TABLE IF EXISTS `venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `venta` (
  `numero_venta` int(11) NOT NULL AUTO_INCREMENT,
  `total` float DEFAULT NULL,
  `fecha` varchar(45) NOT NULL,
  `cliente_id_cliente` int(11) DEFAULT NULL,
  PRIMARY KEY (`numero_venta`),
  KEY `fk_venta_cliente1_idx` (`cliente_id_cliente`),
  CONSTRAINT `fk_venta_cliente1` FOREIGN KEY (`cliente_id_cliente`) REFERENCES `cliente` (`id_cliente`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta`
--

LOCK TABLES `venta` WRITE;
/*!40000 ALTER TABLE `venta` DISABLE KEYS */;
INSERT INTO `venta` VALUES (6,6.2,'18/06/2019',NULL),(7,11.9,'18/06/2019',NULL),(8,3.6,'18/06/2019',1),(9,2.4,'18/06/2019',NULL),(10,2.3,'18/06/2019',1),(11,1.2,'23/05/1982',NULL),(12,6.6,'20/06/2019',NULL),(13,4.5,'20/06/2019',NULL),(14,3.6,'20/06/2019',NULL),(15,2.3,'20/06/2019',1),(16,0,'20/06/2019',NULL),(17,2.3,'20/06/2019',NULL),(18,2.3,'20/06/2019',2),(19,3.6,'20/06/2019',NULL),(20,3.3,'20/06/2019',NULL),(21,3.3,'20/06/2019',NULL),(22,2.2,'20/06/2019',NULL),(23,2.2,'20/06/2019',NULL),(24,3.3,'20/06/2019',NULL),(25,3.3,'20/06/2019',NULL),(26,38.7,'20/06/2019',2),(27,16.4,'20/06/2019',NULL),(28,1.1,'20/06/2019',NULL),(29,11,'20/06/2019',NULL),(30,12.1,'20/06/2019',NULL),(31,21.1,'20/06/2019',2),(32,64.9,'20/06/2019',NULL),(33,16.2,'20/06/2019',NULL),(34,6.2,'20/06/2019',NULL),(35,12,'20/06/2019',NULL),(36,4.7,'20/06/2019',NULL);
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-06-20 12:11:41
