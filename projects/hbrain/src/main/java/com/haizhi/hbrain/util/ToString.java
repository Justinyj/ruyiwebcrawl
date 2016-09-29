/**
* @Title: ToString.java
* @Description: TODO
* @author: calvin
* @date: 2015年11月3日 下午2:18:55
* Copyright: Copyright (c) 2013
* @version: 1.0
*/
package com.haizhi.hbrain.util;

import java.io.Serializable;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

/**
 * @author: calvin
 * @Description: 类打印器
 * @date: 2015年11月3日 下午2:18:55
 */
public class ToString implements Serializable {

	private static final long serialVersionUID = 2916569593087369596L;
	
	private static Map<Class<?>, Field[]> filedMap = new HashMap<Class<?>, Field[]>();
	
	@Override
	public String toString() {
		Field[] fileds = null;
		if (filedMap.containsKey(getClass())) {
			fileds = filedMap.get(getClass());
		}
		else {
			fileds = getClass().getDeclaredFields();
			for(Field field : fileds) {
				field.setAccessible(true);
			}
			filedMap.put(getClass(), fileds);
		}
		StringBuffer sb = new StringBuffer("{");
		for(int i = 0 ; i < fileds.length ; i ++) {
			Field field = fileds[i];
			if (field.getName().equals("serialVersionUID")) {
				continue;
			}
			try {
				Object value = field.get(this);
				sb.append(String.format("%s: %s", field.getName(), value));
				if (i != fileds.length - 1) {
					sb.append(", ");
				}
			} catch (IllegalArgumentException e) {
				e.printStackTrace();
			} catch (IllegalAccessException e) {
				e.printStackTrace();
			}
		}
		sb.append("}");
		return sb.toString();
	}

}
