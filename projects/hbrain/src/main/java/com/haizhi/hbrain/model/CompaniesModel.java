package com.haizhi.hbrain.model;

import com.haizhi.hbrain.util.ToString;
import org.springframework.data.annotation.Id;

import java.util.List;
import java.util.Map;

public class CompaniesModel extends ToString {

	private static final long serialVersionUID = -4327265699911703814L;

	@Id
	private String id;
	private String srank;
	private String nid;
	private String gid;
	private List<String> alias;
	private List<Map<String, String>> claims;
	private String createdTime;
	private String updatedTime;
	private String deletedTime;
	private Map<String, String> source;
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getSrank() {
		return srank;
	}
	public String getNid() {
		return nid;
	}
	public void setNid(String nid) {
		this.nid = nid;
	}
	public String getGid() {
		return gid;
	}
	public void setGid(String gid) {
		this.gid = gid;
	}
	public void setSrank(String srank) {
		this.srank = srank;
	}
	public List<String> getAlias() {
		return alias;
	}
	public void setAlias(List<String> alias) {
		this.alias = alias;
	}
	public List<Map<String, String>> getClaims() {
		return claims;
	}
	public void setClaims(List<Map<String, String>> claims) {
		this.claims = claims;
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
