-- Extrait synthétique au format dump SemMedDB (table PREDICATION, 12 colonnes).
-- Couvre : arêtes valides, gène avec Entrez encodé (C…|1017), guillemet échappé,
-- prédicat négatif (NEG_), prédicat hors ensemble (PROCESS_OF), hub vide (C0007634).
INSERT INTO `PREDICATION` VALUES (1,10,'23000001','INHIBITS','C0017337|1017','CDKN2A gene','gngm',1,'C0018670','Head, and neck neoplasm','dsyn',0),(2,11,'23000002','PARTICIPATES_IN','C0017337|1017','CDKN2A','gngm',1,'C0032131','Apoptotic pathway','moft',0);
INSERT INTO `PREDICATION` VALUES (3,12,'23000003','NEG_STIMULATES','C0000001','GeneA','gngm',1,'C0000002','DiseaseB','dsyn',0),(4,13,'23000004','PROCESS_OF','C0000003','GeneX','gngm',1,'C0000004','DiseaseY','dsyn',0);
INSERT INTO `PREDICATION` VALUES (5,14,'23000005','PART_OF','C0007634','Cells','cell',1,'C0700198','Brain region','bpoc',0),(6,15,'23000006','ASSOCIATED_WITH','C0000010','Beta-amyloid','aapp',1,'C0002395','Alzheimer\'s disease','dsyn',0);
