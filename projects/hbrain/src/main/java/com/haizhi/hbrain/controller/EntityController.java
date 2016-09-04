package com.haizhi.hbrain.controller;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.lang3.StringUtils;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.haizhi.hbrain.model.EntityModel;
import com.haizhi.hbrain.model.NodeModel;
import com.haizhi.hbrain.util.DateTimeUtils;
import com.haizhi.hbrain.util.SmartvApiResult;


@RestController
public class EntityController extends BaseController{
	
	//数据定义接口
	@RequestMapping(value="api/v1/desc",method = RequestMethod.GET)
	public void findHData(@RequestParam(required = false,defaultValue = "0") int offset,@RequestParam(required = false,defaultValue = "20")int limit,
			@RequestParam(required = false)String q,HttpServletRequest request, HttpServletResponse response) throws Exception {
		
		if(mongoTemplate==null){
			SmartvApiResult.writeResponseException(request, response, new Exception("数据库链接失败,error"));
		}
		if(StringUtils.isBlank(q)){
			SmartvApiResult.writeResponseException(request, response, new Exception("  q is null!"));
		}
		
		Query query = new Query();
		List<String> list =new ArrayList<>();
		
		//防止乱码
		q= new String(q.getBytes("UTF-8"), "UTF-8");
		for (String string : q.split(",")) {
			list.add(string);
		}
		query.addCriteria(new Criteria("alias").in(list));
		
		query.skip(offset).limit(limit);
		
		List<EntityModel> lists=mongoTemplate.find(query,EntityModel.class,"entity");
		System.out.println("lists="+lists.size());
		for (EntityModel entity : lists) {
			entity.setNid(null);
			entity.setGid(null);
			entity.setFormat("表格");
			entity.setTotal(entity.getClaims()!=null?entity.getClaims().size():0);
			if(entity.getClaims()!=null && entity.getClaims().size()>0){
				List<String> headList=new ArrayList<>();
				headList.add("属性名");
				headList.add("属性值");
				entity.setHeaders(headList);
			}
			entity.setCreatedTime(DateTimeUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(DateTimeUtils.parseInterISODate(entity.getUpdatedTime()));
			
		}
		SmartvApiResult.writeResponseOk(request, response, lists);//"数据库连接成功,success");
	}
	
	//数据价值接口
	@RequestMapping(value="api/v1/hprice",method = RequestMethod.GET)
	public void getHPrice(@RequestParam(required = false)String q,@RequestParam(required = false)String series,@RequestParam(required = false,defaultValue = "0") int offset,@RequestParam(required = false,defaultValue = "20")int limit,
			HttpServletRequest request, HttpServletResponse response) throws Exception {
		if(mongoTemplate==null){
			SmartvApiResult.writeResponseException(request, response, new Exception("数据库链接失败,error"));
		}
		
		Query query = new Query().skip(offset).limit(limit);
		List<String> list =new ArrayList<>();
		List<NodeModel> lists=null;
		if(StringUtils.isNoneBlank(q)){
			//防止乱码
			q= new String(q.getBytes("UTF-8"), "UTF-8");
			for (String string : q.split(",")) {
				list.add(string);
			}
			query.addCriteria(new Criteria("tags").all(list));
		}else if(StringUtils.isNoneBlank(series)){
			query.addCriteria(new Criteria("series").is(series));
		}else{
			SmartvApiResult.writeResponseException(request, response, new Exception("  q is null!"));
		}
		lists=mongoTemplate.find(query,NodeModel.class,"node");
		SmartvApiResult.writeResponseOk(request, response, lists);
	}
	
	//数据价值接口
	@RequestMapping(value="debug/version",method = RequestMethod.GET)
	public void version(HttpServletRequest request, HttpServletResponse response) throws Exception {
		SmartvApiResult.writeResponseOk(request, response,new Date());
	}
	
	
}
