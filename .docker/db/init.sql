USE db;

CREATE TABLE driven_distances (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `vehicle_id` VARCHAR(255) NOT NULL,
    `day` DATE NOT NULL,
    `km_driven` FLOAT NOT NULL,
    PRIMARY KEY (id)
);
