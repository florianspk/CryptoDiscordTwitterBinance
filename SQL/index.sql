CREATE TABLE `twitter_analyze` (
  `ref_twitter` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY ,
  `user_id` varchar(255)  NOT NULL ,
  `content` varchar(255) NOT NULL ,
  `crypto` varchar(255) NOT NULL ,
  `bot_good_sentence` varchar(255) NOT NULL,
  `date_post` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;





