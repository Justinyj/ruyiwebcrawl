package com.haizhi.hbrain.util;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import com.smartv.common.core.ApiCalendar;
import com.smartv.common.ext.ApiGson;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.*;

public class SmartvApiResult {
	private static final Logger log = Logger.getLogger(SmartvApiResult.class);

	private int code;
	private String message;
	private Object result;
	private int total;
	private long duration;
	private String totalCount;
	
	public SmartvApiResult() {

	}

	public SmartvApiResult(int code, String msg, Object result) {
		this.code = code;
		this.message = msg;
		this.result = result;
	}
	public SmartvApiResult(int code, String msg, Object result, int total) {
		this.code = code;
		this.message = msg;
		this.result = result;
		this.total=total;
	}
	public SmartvApiResult(int code, String msg, Object result, int total, String totalCount) {
		this.code = code;
		this.message = msg;
		this.result = result;
		this.total=total;
		this.totalCount=totalCount;
	}
	public SmartvApiResult(int code, String msg, Object result, int total, long duration, String totalCount) {
		this.code = code;
		this.message = msg;
		this.result = result;
		this.total=total;
		this.duration=duration;
		this.totalCount=totalCount;
	}

	public static String successForObj(Object result) {
		if (null == result) {
			SmartvApiResult res = new SmartvApiResult(2, "未获取到数据", result);// 0:成功
			return ApiGson.toJson(res);
		} else if (result instanceof JsonElement) {
			JsonObject ret = new JsonObject();
			ret.addProperty("code", 0);
			ret.addProperty("msg", "成功");
			ret.add("result", (JsonElement) result);
			return ApiGson.toString(ret);
			// }else if (result instanceof String){
			// return (String) result;
		} else if(result instanceof List){
			SmartvApiResult res = new SmartvApiResult(0, "成功", result, ((List<?>) result).size());// 0:成功
			return ApiGson.toJson(res);
		} else {
			SmartvApiResult res = new SmartvApiResult(0, "成功", result);// 0:成功
			return ApiGson.toJson(res);
		}
	}

	public static String successForObj(Object result, String totalCount) {
		if (null == result) {
			SmartvApiResult res = new SmartvApiResult(2, "未获取到数据", result, 0, totalCount);// 0:成功
			return ApiGson.toJson(res);
		} else if (result instanceof JsonElement) {
			JsonObject ret = new JsonObject();
			ret.addProperty("code", 0);
			ret.addProperty("msg", "成功");
            ret.addProperty("totalCount", 1);
			ret.add("result", (JsonElement) result);
			return ApiGson.toString(ret);
			// }else if (result instanceof String){
			// return (String) result;
		} else if(result instanceof List){
			SmartvApiResult res = new SmartvApiResult(0, "成功", result, ((List<?>) result).size(), totalCount);// 0:成功
			return ApiGson.toJson(res);
		} else {
			SmartvApiResult res = new SmartvApiResult(0, "成功", result, 0, totalCount);// 0:成功
			return ApiGson.toJson(res);
		}
	}


	public static String successForObj(Object result, long duration, String totalCount) {
		if (null == result) {
			SmartvApiResult res = new SmartvApiResult(2, "未获取到数据", result, 0, duration, totalCount);// 0:成功
			return ApiGson.toJson(res);
		} else if (result instanceof JsonElement) {
			JsonObject ret = new JsonObject();
			ret.addProperty("code", 0);
			ret.addProperty("msg", "成功");
			ret.addProperty("duration", duration);
			ret.addProperty("totalCount", 1);
			ret.add("result", (JsonElement) result);
			return ApiGson.toString(ret);
			// }else if (result instanceof String){
			// return (String) result;
		} else if(result instanceof List){
			SmartvApiResult res = new SmartvApiResult(0, "成功", result, ((List<?>) result).size(), duration, totalCount);
			return ApiGson.toJson(res);
		} else {
			SmartvApiResult res = new SmartvApiResult(0, "成功", result, 0, duration, totalCount);
			return ApiGson.toJson(res);
		}
	}

	public static String success(String msg) {
		SmartvApiResult result = new SmartvApiResult(0, msg, null);// 0:成功
		return ApiGson.toJson(result);
	}

	public static String failure(String msg) {
		SmartvApiResult result = new SmartvApiResult(1, msg, null);// 1:失败
		return ApiGson.toJson(result);
	}

	public int getCode() {
		return code;
	}

	public void setCode(int code) {
		this.code = code;
	}

	public String getMessage() {
		return message;
	}

	public void setMessage(String msg) {
		this.message = msg;
	}

	public Object getResult() {
		return result;
	}

	public void setResult(Object result) {
		this.result = result;
	}
	public int getTotal() {
		return total;
	}

	public void setTotal(int total) {
		this.total = total;
	}
	@SuppressWarnings("unchecked")
	public static JsonObject packInput(HttpServletRequest request, JsonObject metadata, String... args) {
		// produce output
		JsonObject ret = new JsonObject();

		ret.add("metadata", metadata);

		JsonObject httpHeaders = new JsonObject();
		Enumeration<String> enumHeader = request.getHeaderNames();
		while (enumHeader.hasMoreElements()) {
			String h = enumHeader.nextElement();
			httpHeaders.addProperty(h, request.getHeader(h));
		}
		ret.add("reuqest_headers", httpHeaders);

		JsonObject httpParams = new JsonObject();
		JsonObject httpParamsExt = new JsonObject();
		Enumeration<String> enumParams = request.getParameterNames();
		while (enumParams.hasMoreElements()) {
			String h = enumParams.nextElement();
			String[] values = request.getParameterValues(h);
			httpParams.addProperty(h, values[0]);
			if (values.length > 1) {
				JsonArray xValues = new JsonArray();
				for (String v : values) {
					xValues.add(new JsonPrimitive(v));
				}
				httpParamsExt.add(h, xValues);
			}
		}
		ret.add("request_params", httpParams);
		ret.add("request_params_ext", httpParamsExt);

		JsonObject httpMisc = new JsonObject();
		httpMisc.addProperty("local_address", request.getLocalAddr());
		httpMisc.addProperty("remote_address", request.getRemoteAddr());
		httpMisc.addProperty("local_name", request.getLocalName());
		httpMisc.addProperty("context_path", request.getContextPath());
		httpMisc.addProperty("servlet_path", request.getServletPath());
		httpMisc.addProperty("query_string", request.getQueryString());
		// httpMisc.addProperty("everything",GsonUtil.toJson(request));
		ret.add("request_misc", httpMisc);

		if (null != args) {
			JsonObject params = new JsonObject();
			for (String s : args) {
				if (!StringUtils.isEmpty(s)) {
					String[] pv = s.split(":", 1);
					if (null != pv && pv.length == 2) {
						params.addProperty(pv[0], pv[1]);
					}
				}
			}
			ret.add("params", params);
		}

		return ret;
	}

	public static JsonObject packMetadata(String type, String release_version, String build_version) {
		Date now = new Date();
		JsonObject ret = new JsonObject();
		ret.addProperty("uuid", UUID.randomUUID().toString());
		ret.addProperty("timestamp", now.getTime());
		ret.addProperty("tzid", Calendar.getInstance().getTimeZone().getID());
		ret.addProperty("updated", ApiCalendar.getXmlDatetime(now, Calendar.getInstance().getTimeZone()));
		ret.addProperty("type", type);
		ret.addProperty("release_vesrion", release_version);
		ret.addProperty("build_version", build_version);

		return ret;
	}

	public static void writeResponse(HttpServletRequest request, HttpServletResponse response, String output)
			throws IOException {
		if (output == null)
			return;

		log.info(output);

		response.setContentType("text/plain");
		response.setCharacterEncoding("UTF-8");
		PrintWriter writer = response.getWriter();
		if (writer != null) {
			writer.write(output);
			writer.close();
		}
	}

	public static void writeResponseException(HttpServletRequest request, HttpServletResponse response, Exception e) {
		log.error(e.getMessage(), e);
		try {
			writeResponse(request, response, SmartvApiResult.failure("失败" + e.getMessage()));
		} catch (Exception e1) {
			try {
				writeResponse(request, response, SmartvApiResult.failure("失败+失败"));
			} catch (IOException e2) {
				e2.printStackTrace();
			}
		}
	}

	public static void writeResponseOk(HttpServletRequest request, HttpServletResponse response, Object output)
			throws IOException {
		writeResponse(request, response, SmartvApiResult.successForObj(output));
	}

    public static void writeResponseOk(HttpServletRequest request, HttpServletResponse response, Object output, String totalCount)
            throws IOException {
        writeResponse(request, response, SmartvApiResult.successForObj(output, totalCount));
    }

	public static void writeResponseOk(HttpServletRequest request, HttpServletResponse response, Object output, long duration, String totalCount)
			throws IOException {
		writeResponse(request, response, SmartvApiResult.successForObj(output, duration, totalCount));
	}
}
