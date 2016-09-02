package com.haizhi.hbrain.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;

public class BaseController {

	@Autowired
	public MongoTemplate mongoTemplate;
}
