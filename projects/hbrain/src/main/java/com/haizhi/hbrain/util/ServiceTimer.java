/**
 * TODO
 * @Title: ServiceTimer.java
 * @author: calvin
 * @date: 2016年1月26日 下午5:42:07
 * Copyright: Copyright (c) 2013
 * @version: 1.0
*/
package com.haizhi.hbrain.util;

import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;
import org.apache.commons.lang3.time.StopWatch;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;

/**
 * 服务调用时间统计
 * 
 * @author: calvin
 * @date: 2016年1月26日 下午5:42:07
 */
public class ServiceTimer implements MethodInterceptor {

	private Log log = LogFactory.getLog(ServiceTimer.class);

	private static Map<Method, Class<?>[]> parameterMap = new HashMap<Method, Class<?>[]>();

	/**
	 * 统计时长
	 * 
	 * @Title: invoke
	 * @Description: 统计时长
	 * @param invocation
	 * @return
	 * @throws Throwable
	 */
	@Override
	public Object invoke(MethodInvocation invocation) throws Throwable {
		Object result = null;
		if (log.isInfoEnabled()) {
			StopWatch stopWatch = new StopWatch();
			stopWatch.start();
			result = invocation.proceed();
			stopWatch.stop();

			Class<?>[] clazz = null;
			Method m = invocation.getMethod();
			if (!parameterMap.containsKey(m)) {
				clazz = m.getParameterTypes();
				parameterMap.put(m, clazz);
			} else {
				clazz = parameterMap.get(m);
			}

			Object[] args = invocation.getArguments();
			StringBuffer sb = new StringBuffer();
			int i = 0;
			for (; i < clazz.length - 1; i++) {
				sb.append(String.format("%s:%s,", clazz[i].getSimpleName(), args[i]));
			}
			sb.append(String.format("%s:%s", clazz[i].getSimpleName(), args[i]));

			if (log.isDebugEnabled()) {
				log.info(String.format("RPC - %s %s.%s(%s) takes %d ms => %s",
						invocation.getMethod().getReturnType().getSimpleName(),
						invocation.getMethod().getDeclaringClass().getSimpleName(), invocation.getMethod().getName(),
						sb, stopWatch.getTime(), result));
			} else {
				log.info(String.format("RPC - %s %s.%s(%s) takes %d ms",
						invocation.getMethod().getReturnType().getSimpleName(),
						invocation.getMethod().getDeclaringClass().getSimpleName(), invocation.getMethod().getName(),
						sb, stopWatch.getTime()));
			}

			stopWatch = null;
		} else {
			result = invocation.proceed();
		}
		return result;
	}

}
