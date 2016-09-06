package com.haizhi.hbrain.controller;

import com.haizhi.hbrain.model.EnterprisesModel;
import com.haizhi.hbrain.model.EntitiesModel;
import com.haizhi.hbrain.model.PriceModel;
import com.haizhi.hbrain.util.APIUtils;
import com.haizhi.hbrain.util.SmartvApiResult;
import org.apache.commons.lang3.StringUtils;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.Sort.Order;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Date;
import java.util.List;


@RestController
public class HbrainAPIController extends BaseController{
	
	//数据定义接口
	@RequestMapping(value="api/v1/entities",method = RequestMethod.GET)
	public void findHData(@RequestParam(required = false,defaultValue = "0") int offset,@RequestParam(required = false,defaultValue = "20")int limit,
			@RequestParam(required = false)String q,HttpServletRequest request, HttpServletResponse response) throws Exception {
		
		if(mongoTemplate==null){
			SmartvApiResult.writeResponseException(request, response, new Exception("数据库链接失败,error"));
		}
		if(StringUtils.isBlank(q)){
			SmartvApiResult.writeResponseException(request, response, new Exception("  q or types is null!"));
		}
		
		Query query = APIUtils.constructQuery(q, offset, limit).with(new Sort(new Order(Direction.DESC,"source.confidence")));
		
		List<EntitiesModel> lists=mongoTemplate.find(query,EntitiesModel.class,"entities");
		for (EntitiesModel entity : lists) {
			entity.setNid(null);
			entity.setGid(null);
			entity.setTotal(entity.getClaims()!=null?entity.getClaims().size():0);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		SmartvApiResult.writeResponseOk(request, response, lists);//"数据库连接成功,success");
	}
	
	//数据价值接口
	@RequestMapping(value="api/v1/price",method = RequestMethod.GET)
	public void getHPrice(@RequestParam(required = false)String q,@RequestParam(required = false,defaultValue = "0") int offset,@RequestParam(required = false,defaultValue = "20")int limit,
			HttpServletRequest request, HttpServletResponse response) throws Exception {
		if(mongoTemplate==null){
			SmartvApiResult.writeResponseException(request, response, new Exception("数据库链接失败,error"));
		}
		if(StringUtils.isBlank(q)){
			SmartvApiResult.writeResponseException(request, response, new Exception("  q is null!"));
		}

		Query query = APIUtils.constructQuery(q, offset, limit).with(new Sort(new Order(Direction.DESC,"updatedTime")));
		
		List<PriceModel> lists = mongoTemplate.find(query,PriceModel.class,"price");
		for (PriceModel entity : lists) {
			entity.setRid(null);
			entity.setGid(null);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		SmartvApiResult.writeResponseOk(request, response, lists);
	}
	
	
	//知识图谱数据企业接口
	@RequestMapping(value="api/v1/enterprises",method = RequestMethod.GET)
	public void enterprises(@RequestParam(required = false)String q,@RequestParam(required = false,defaultValue = "0") int offset,
			@RequestParam(required = false,defaultValue = "20")int limit,
			HttpServletRequest request, HttpServletResponse response) throws Exception {
		if(mongoTemplate==null){
				SmartvApiResult.writeResponseException(request, response, new Exception("数据库链接失败,error"));
			}
		if(StringUtils.isBlank(q)){
			SmartvApiResult.writeResponseException(request, response, new Exception("  q is null!"));
		}

		Query query = APIUtils.constructQuery(q, offset, limit);
		List<EnterprisesModel> lists = mongoTemplate.find(query,EnterprisesModel.class,"enterprises");
		for (EnterprisesModel entity : lists) {
			entity.setNid(null);
			entity.setGid(null);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		SmartvApiResult.writeResponseOk(request, response, lists);
	}
	
	
	//数据价值接口
	@RequestMapping(value="debug/version",method = RequestMethod.GET)
	public void version(HttpServletRequest request, HttpServletResponse response) throws Exception {
		SmartvApiResult.writeResponseOk(request, response,new Date());
	}
}
