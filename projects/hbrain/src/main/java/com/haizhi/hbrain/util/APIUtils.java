package com.haizhi.hbrain.util;

import org.apache.commons.lang3.StringUtils;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class APIUtils {

	@SuppressWarnings("deprecation")
	public static String parseInterISODate(String date){
		if(StringUtils.isBlank(date)){
			return null;
		}
		Date d = new Date(date);
		SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SS");//其中yyyy-MM-dd是你要表示的格式 
		// 可以任意组合，不限个数和次序；具体表示为：MM-month,dd-day,yyyy-year;kk-hour,mm-minute,ss-second; 
		String str = sdf.format(d);
		str = str.split(" ")[0] + "T" + str.split(" ")[1] + "Z";
		return str;
	}

	public static List<Criteria> parseTimeRange(String recordDate) {
		List<Criteria> criterias = new ArrayList<>();

		String begin = recordDate.split("TO")[0];
		if (begin.startsWith("[")) {
			begin = begin.substring(1).trim();
			if (begin.equals("*")) {
			} else {
				criterias.add(new Criteria("recordDate").gte(begin));
			}
		} else if (begin.startsWith("{")) {
			begin = begin.substring(1).trim();
			if (begin.equals("*")) {
			} else {
				criterias.add(new Criteria("recordDate").gt(begin));
			}
		}
		String end = recordDate.split("TO")[1];
		if (end.endsWith("]")) {
			end = end.substring(0, end.length() - 1).trim();
			if (end.equals("*")) {
			} else {
				criterias.add(new Criteria("recordDate").lte(end));
			}
		} else if (end.endsWith("}")) {
			end = end.substring(0, end.length() - 1).trim();
			if (end.equals("*")) {
			} else {
				criterias.add(new Criteria("recordDate").gt(end));
			}
		}
		return criterias;
	}

	public static List<Criteria> constructSubQuery(String sub) {
		String key = null;
		List<Criteria> criterias = new ArrayList<>();
		List<String> vlauesList = new ArrayList<>();
		String[] strings = null;
		//System.out.println("sub: " + sub);

		if (sub.contains("AND")) {
			strings = sub.split("AND");
			for (String string : strings) {
				key = string.trim().split(":")[0];
				vlauesList.add(string.trim().split(":")[1]);
			}
			criterias.add(new Criteria(key).all(vlauesList));
		} else if (sub.contains("OR")) {
			strings = sub.split("OR");
			for (String string : strings) {
				key = string.trim().split(":")[0];
				vlauesList.add(string.trim().split(":")[1]);
			}
			criterias.add(new Criteria(key).in(vlauesList));
		} else {
			if (sub.contains(":")) {
				key = sub.trim().split(":")[0];
				if (sub.startsWith("recordDate")) {
					List<Criteria> subCriterias = parseTimeRange(sub.trim().split(":")[1]);
					for (Criteria criteria : subCriterias) {
						criterias.add(criteria);
					}
				} else {

					vlauesList.add(sub.trim().split(":")[1]);
				}
				criterias.add(new Criteria(key).in(vlauesList));
			}
		}
		return criterias;
	}

	public static Query findSubQueries(String q, Query query) {
		//括号的部分抽出来，当做子查询
		if (StringUtils.isBlank(q)) {
			return null;
		}
		int end;
		q = q.trim();

		while (StringUtils.isNotBlank(q)) {
			String pre = "";
			if (q.startsWith("AND")) {
				pre = "AND";
				q = q.substring(3).trim();
			} else if (q.startsWith("OR")) {
				pre = "OR"; // TODO parsing
				q = q.substring(2).trim();
			}

			//System.out.println("query without pre: " + q);
			if (q.startsWith("(")) {
				end = q.indexOf(')');
				String sub = q.substring(1, end);
				if (pre == "" || pre == "AND") {
					for (Criteria criteria: constructSubQuery(sub)) {
						query.addCriteria(criteria);
					}
				}
				q = q.substring(end + 1).trim();
			} else {
				end = q.indexOf("AND");
				if (end == -1) {
					end = q.indexOf("OR");
					if (end == -1) {
						end = q.length();
					}
				}
				String sub = q.substring(0, end).trim();
				if (pre == "" || pre == "AND") {
					for (Criteria criteria: constructSubQuery(sub)) {
						query.addCriteria(criteria);
					}
				}
				q = q.substring(end).trim();
			}
			//System.out.println("next sub_q: " + q);
		}
		return query;
	}

	public static Query constructQuery(String q) {
		/*
			hypothesis: 括号里面的query字段都是一个字段，相邻的同一个字段必须加括号，
				最外层相当于一个隐去的括号，这样就很容易跟mongodb的query对应起来。
			q=(tags:豆油 AND tags:广东广州粮油批发交易市场) AND recordDate:[2016-08-02 TO 2016-09-02}
			db.price.find({tags: {$all: ['豆油', '广东广州粮油批发交易市场']}, recordDate: {$gte: '2016-08-02', $lt: '2016-09-02'}})

			q=(tags:豆油 AND tags:广东广州粮油批发交易市场) OR recordDate:[2016-08-02 TO 2016-09-02}
			db.price.find({$or: [{tags: {$all: ['豆油', '广东广州粮油批发交易市场']}}, {recordDate: {$gte: '2016-08-02', $lt: '2016-09-02'}}]})
		*/
		Query query = null;
		try {
			//防止乱码
			q = new String(q.getBytes("UTF-8"), "UTF-8");
			query = new Query().addCriteria(new Criteria("deletedTime").is(null));
			
			if (StringUtils.isNotBlank(q)) {
				findSubQueries(q, query);
			} else {
				System.out.println("query is blank: " + q);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		return query;
	}
}
