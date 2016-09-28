package com.haizhi.hbrain.controller;

import com.haizhi.hbrain.model.*;
import com.haizhi.hbrain.util.APIUtils;
import com.haizhi.hbrain.util.SmartvApiResult;
import org.apache.commons.lang3.StringUtils;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.domain.Sort.Order;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


@RestController
public class HbrainAPIController extends BaseController {

	@RequestMapping(value="api/v1/{types}", method=RequestMethod.GET)
	public void apiInterface(@PathVariable(required = true) String types,
							 @RequestParam(required = false) String q,
							 @RequestParam(required = false, defaultValue = "0") int offset,
							 @RequestParam(required = false, defaultValue = "20") int limit,
							 HttpServletRequest request, HttpServletResponse response) throws Exception {
		if (mongoTemplate == null) {
			SmartvApiResult.writeResponseException(request, response, new Exception("error: 数据库连接失败"));
		}
		if (StringUtils.isBlank(q)) {
			SmartvApiResult.writeResponseException(request, response, new Exception("q is null!"));
		}

		long start = System.currentTimeMillis();
		List<?> lists = null;
		switch (types) {
			case "entities":
				lists = findEntities(q, offset, limit);
				break;
			case "price":
				Map<String, List<PriceModel>> maps = findPrice(q, offset, limit);
				String totalCount = null;
				for (String key : maps.keySet()){
					lists = maps.get(key);
					break;
				}
				SmartvApiResult.writeResponseOk(request, response, lists, totalCount);
				return;
			case "pricemeta":
				break;
			case "companies":
				lists = findCompanies(q, offset, limit);
				break;
			case "news":
				lists = findNews(q, offset, limit);
				break;
			case "records":
				lists = findRecords(q, offset, limit);
				break;
			default:
				throw new IllegalArgumentException("types of API error");

		}
		long duration = System.currentTimeMillis() - start;
		SmartvApiResult.writeResponseOk(request, response, lists);
	}
	
	//数据定义接口
	public List<EntitiesModel> findEntities(String q,
                             				int offset,
                             				int limit) {
		Query query = APIUtils.constructQuery(q).skip(offset).limit(limit).with(new Sort(new Order(Direction.DESC, "source.confidence")));
		
		List<EntitiesModel> lists = mongoTemplate.find(query, EntitiesModel.class, "entities");
		for (EntitiesModel entity : lists) {
			entity.setNid(null);
			entity.setGid(null);
			entity.setTotalClaim(entity.getClaims()!=null?entity.getClaims().size():0);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		return lists;
	}
	
	//数据价格接口
	public Map<String, List<PriceModel>> findPrice(String q,
												   int offset,
												   int limit) {
		Map<String, List<PriceModel>> maps = new HashMap<String, List<PriceModel>>();

		Query query = APIUtils.constructQuery(q);
		long totalCount = mongoTemplate.count(query, PriceModel.class, "price");
		query.skip(offset).limit(limit).with(new Sort(new Order(Direction.DESC, "recordDate")));
		List<PriceModel> lists = mongoTemplate.find(query, PriceModel.class, "price");
		for (PriceModel entity : lists) {
			entity.setRid(null);
			entity.setGid(null);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		maps.put(Long.toString(totalCount), lists);
		return maps;
	}
	
	
	//知识图谱数据企业接口

	public List<CompaniesModel> findCompanies(String q,
                                              int offset,
			                                  int limit) {
		Query query = APIUtils.constructQuery(q).skip(offset).limit(limit);
		List<CompaniesModel> lists = mongoTemplate.find(query, CompaniesModel.class, "companies");
		for (CompaniesModel entity : lists) {
			entity.setNid(null);
			entity.setGid(null);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		return lists;
	}
	

	//知识图谱新闻接口
    public List<NewsModel> findNews(String q,
                     				int offset,
                     				int limit) {
        Query query = APIUtils.constructQuery(q).skip(offset).limit(limit).with(new Sort(new Order(Direction.DESC, "updatedTime")));
        List<NewsModel> lists = mongoTemplate.find(query, NewsModel.class, "news");
        for (NewsModel entity : lists) {
            entity.setRid(null);
            entity.setGid(null);
            entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
            entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
        }
        return lists;
    }


	public List<RecordsModel> findRecords(String q,
						                  int offset,
						                  int limit) {
		Query query = APIUtils.constructQuery(q).skip(offset).limit(limit).with(new Sort(new Order(Direction.DESC, "updatedTime")));

		List<RecordsModel> lists = mongoTemplate.find(query, RecordsModel.class, "records");
		for (RecordsModel entity : lists) {
			entity.setRid(null);
			entity.setGid(null);
			entity.setCreatedTime(APIUtils.parseInterISODate(entity.getCreatedTime()));
			entity.setUpdatedTime(APIUtils.parseInterISODate(entity.getUpdatedTime()));
		}
		return lists;
	}

	//数据价值接口
	@RequestMapping(value="debug/version",method = RequestMethod.GET)
	public void version(HttpServletRequest request, HttpServletResponse response) throws Exception {
		SmartvApiResult.writeResponseOk(request, response, new Date());
	}
}
