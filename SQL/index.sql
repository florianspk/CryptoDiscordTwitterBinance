CREATE TABLE `twitter_popular_tags` (
  `twitter_popular_tags_id` int(11) NOT NULL,
  `hashtag` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `location_type` varchar(255) DEFAULT NULL,
  `popular_date_time` datetime DEFAULT NULL,
  `popular_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


ALTER TABLE `twitter_popular_tags`
  ADD PRIMARY KEY (`twitter_popular_tags_id`),
  ADD KEY `hashtag` (`hashtag`),
  ADD KEY `popular_date_time` (`popular_date_time`),
  ADD KEY `popular date` (`popular_date`);


ALTER TABLE `twitter_popular_tags`
  MODIFY `twitter_popular_tags_id` int(11) NOT NULL AUTO_INCREMENT;