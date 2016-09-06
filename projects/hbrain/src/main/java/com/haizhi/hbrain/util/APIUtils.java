package com.haizhi.hbrain.util;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.apache.commons.lang3.StringUtils;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;

public class APIUtils {

	@SuppressWarnings("deprecation")
	public static String parseInterISODate(String date){
		if(StringUtils.isBlank(date)){
			return null;
		}
		Date d = new Date(date);
		SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SS");//其中yyyy-MM-dd是你要表示的格式 
		// 可以任意组合，不限个数和次序；具体表示为：MM-month,dd-day,yyyy-year;kk-hour,mm-minute,ss-second; 
		String str=sdf.format(d); 
		str=str.split(" ")[0]+"T"+str.split(" ")[1]+"Z";
		return str;
	}
	
	public static Query constructQuery(String q,int offset,int limit){
		List<String> vlauesList =new ArrayList<>();
		String key=null;
		Query query = null;
		try {
			//防止乱码
			q= new String(q.getBytes("UTF-8"), "UTF-8");
			query = new Query().skip(offset).limit(limit).addCriteria(new Criteria("deletedTime").is(null));
			
			if(StringUtils.isNoneBlank(q)){
				String[] strings=null;
				if(q.contains("AND")){
					strings=q.split("AND");
					for (String string : strings) {
						if(key==null){
							key=string.trim().split(":")[0];
						}
						vlauesList.add(string.trim().split(":")[1]);
					}
					query.addCriteria(new Criteria(key).all(vlauesList));
				}else if(q.contains("OR")){
					strings=q.split("OR");
					for (String string : strings) {
						if(key==null){
							key=string.trim().split(":")[0];
						}
						vlauesList.add(string.trim().split(":")[1]);
					}
					query.addCriteria(new Criteria(key).in(vlauesList));
				}else{
					if(q.contains(":")){
						if(key==null){
							key=q.trim().split(":")[0];
						}
						vlauesList.add(q.trim().split(":")[1]);
						query.addCriteria(new Criteria(key).in(vlauesList));
					}
				}
			}
			System.out.println("key="+key+",vlauesList="+vlauesList);
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		return query;
	}
}
