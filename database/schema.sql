CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `counters` (
  `id` varchar(36) NOT NULL,
  `key` varchar(255) NOT NULL,
  `next_index` int(16) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `questions` (
  `id` varchar(36) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `category` varchar(32) NOT NULL,
  `question` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `questions_shuffled` (
  `foreign_id` varchar(36) NOT NULL,
  `order` int(16) NOT NULL,
  `category` varchar(32) NOT NULL,
  `question` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `membership_stats` (
  `id` varchar(36) NOT NULL,
  `category` varchar(32) NOT NULL,
  `role_id` int(16) NOT NULL,
  `role_name` varchar(32) NOT NULL,
  `role_color` int(16) NOT NULL,
  `member_count` int(16) NOT NULL,
  `collection_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `nut` (
  `id` varchar(36) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `channel_id` varchar(20) NOT NULL,
  `message_id` varchar(20) NOT NULL,
  `op_author_id` varchar(20) NOT NULL,
  `content_type` varchar(20) NOT NULL,
  `collection_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/********************
EVENT: COLOR WAR
********************/
CREATE TABLE IF NOT EXISTS `event_colorwar_players` (
  `id` varchar(36) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `team_role_id` varchar(20) NOT NULL,
  `last_paintball_shot` timestamp
);

CREATE TABLE IF NOT EXISTS `event_colorwar_inventory` (
  `id` varchar(36) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `item` varchar(20) NOT NULL,
  `inv_count` varchar(16) NOT NULL,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `event_colorwar_channel_owner` (
  `id` varchar(36) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `channel_id` varchar(20) NOT NULL,
  `owner_team_role_id` varchar(20),
  `paintball_hit_points` int(16) NOT NULL,
  `paintball_production` int(16) NOT NULL,
  `paintball_supply` int(16) NOT NULL,
  `last_resupply` timestamp,
  `last_ownership_update` timestamp,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CREATE TABLE IF NOT EXISTS `event_colorwar_channel_contention` (
--   `id` varchar(36) NOT NULL,
--   `server_id` varchar(20) NOT NULL,
--   `channel_id` varchar(20) NOT NULL,
--   `team_role_id` varchar(20) NOT NULL,
--   `paintball_hit_count` varchar(16) NOT NULL,
--   `paintball_supply` varchar(16) NOT NULL,
--   `last_resupply` timestamp,
--   `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );

/** ACTIONS = PAINTBALLED, GIFTED, GRENADED, CAPTURED **/
CREATE TABLE IF NOT EXISTS `event_colorwar_log` (
  `id` varchar(36) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `channel_id` varchar(20) NOT NULL,
  `message_id` varchar(20) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `action` varchar(20) NOT NULL, 
  `target_type` varchar(20) NOT NULL,
  `target_id` varchar(20) NOT NULL,
  `collection_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `event_colorwar_item_spawn` (
  `id` varchar(36) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `channel_id` varchar(20) NOT NULL,
  `message_id` varchar(20) NOT NULL,
  `item_type` varchar(20) NOT NULL,
  `item_quantity` int(16) NOT NULL,
  `collected_by_user_id` varchar(20),
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);