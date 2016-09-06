package com.haizhi.hbrain.model;

import java.util.List;
import java.util.Map;

import org.springframework.data.annotation.Id;

import com.haizhi.hbrain.util.ToString;

public class PriceModel extends ToString{

	/**
	 * 
	 */
	private static final long serialVersionUID = 4948172401697253231L;
	
	@Id
	private String id;
	private String gid;
	private String rid;
	private String series;
	private String tags;
	private List<Map<String, String>> claims;
	private String createdTime;
	private String updatedTime;
	private String dataSource;
	private String deletedTime;
	private Map<String, String> source;
	public String getId() {
		return id;
	}
	public List<Map<String, String>> getClaims() {
		return claims;
	}
	public void setClaims(List<Map<String, String>> claims) {
		this.claims = claims;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getGid() {
		return gid;
	}
	public void setGid(String gid) {
		this.gid = gid;
	}
	public String getRid() {
		return rid;
	}
	public void setRid(String rid) {
		this.rid = rid;
	}
	public String getSeries() {
		return series;
	}
	public void setSeries(String series) {
		this.series = series;
	}
	public String getTags() {
		return tags;
	}
	public void setTags(String tags) {
		this.tags = tags;
	}
	public String getCreatedTime() {
		return createdTime;
	}
	public void setCreatedTime(String createdTime) {
		this.createdTime = createdTime;
	}
	public String getUpdatedTime() {
		return updatedTime;
	}
	public void setUpdatedTime(String updatedTime) {
		this.updatedTime = updatedTime;
	}
	public String getDataSource() {
		return dataSource;
	}
	public void setDataSource(String dataSource) {
		this.dataSource = dataSource;
	}
	public String getDeletedTime() {
		return deletedTime;
	}
	public void setDeletedTime(String deletedTime) {
		this.deletedTime = deletedTime;
	}
	public Map<String, String> getSource() {
		return source;
	}
	public void setSource(Map<String, String> source) {
		this.source = source;
	}
	
}
