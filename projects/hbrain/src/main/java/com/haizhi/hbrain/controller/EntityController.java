package com.haizhi.hbrain.controller;

import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.haizhi.hbrain.model.Entity;
import com.haizhi.hbrain.util.SmartvApiResult;


@RestController
public class EntityController extends BaseController{
	private Log log=LogFactory.getLog(getClass());
	
	@RequestMapping(value="api/v1/desc",method = RequestMethod.GET)
	public void test(@RequestParam(required = false,defaultValue = "0") int offset,@RequestParam(required = false,defaultValue = "20")int limit,
			HttpServletRequest request, HttpServletResponse response) throws Exception {
		if(mongoTemplate!=null){
			Query query = new Query();
			query.addCriteria(new Criteria("id").is("57c939aafdcdad190ba65a94"));
			List<Entity> lists=mongoTemplate.find(query,Entity.class,"entity");
			log.info("lists="+lists);
			SmartvApiResult.writeResponseOk(request, response, "数据库连接成功,success");
		}else{
			SmartvApiResult.writeResponseOk(request, response, "数据库链接失败,error");
		}
	}
			
}
