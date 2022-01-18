CREATE TABLE `twitter_analyze` (
  `ref_twitter` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY ,
  `id_tweet` varchar(255) NOT NULL ,
  `user_id` int NOT NULL ,
  `content` varchar(255) NOT NULL ,
  `date_post` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;





