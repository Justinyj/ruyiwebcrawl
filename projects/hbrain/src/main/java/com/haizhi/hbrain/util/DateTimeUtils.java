package com.haizhi.hbrain.util;

import java.text.SimpleDateFormat;
import java.util.Date;

public class DateTimeUtils {


	public static String parseInterISODate(String date){
		Date d = new Date(date);
		SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SS");//其中yyyy-MM-dd是你要表示的格式 
		// 可以任意组合，不限个数和次序；具体表示为：MM-month,dd-day,yyyy-year;kk-hour,mm-minute,ss-second; 
		String str=sdf.format(d); 
		str=str.split(" ")[0]+"T"+str.split(" ")[1]+"Z";
		return str;
	}
}
